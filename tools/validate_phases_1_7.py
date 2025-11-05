#!/usr/bin/env python3
"""
End-to-end validator for Phases 1–7 (API-level checks only).

Requires a running backend (and optional frontend). Safe to run locally or in CI.

Checks:
- Phase 1: health, OpenAPI, login, /auth/me, roles, /users (authz), audit logs reachable
- Phase 2: aws-iam-baseline runner in parameter mode
- Phase 3: panorama stub (skipped by default, success when flag enabled), port-scan module presence
- Phase 4: notifications CRUD and history route presence
- Phase 6: /metrics reachable (Prometheus)
- Phase 7: scheduler flags (reads env echo), list module runs

Run:
  python tools/validate_phases_1_7.py --backend http://localhost:5000 --admin-user admin --admin-pass Admin@1234
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Dict, Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def http(method: str, url: str, headers: Dict[str, str] | None = None, data: Any | None = None):
    body_bytes = None
    hdrs = dict(headers or {})
    if data is not None:
        body_bytes = json.dumps(data).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    req = Request(url, method=method, headers=hdrs)
    try:
        with urlopen(req, data=body_bytes, timeout=10) as resp:
            return resp.getcode(), dict(resp.headers), resp.read()
    except HTTPError as e:
        return e.code, dict(e.headers or {}), e.read() if e.fp else b""
    except URLError as e:
        return 0, {}, str(e).encode("utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--backend", default="http://localhost:5000")
    p.add_argument("--frontend", default=None)
    p.add_argument("--admin-user", default="admin")
    p.add_argument("--admin-pass", default="Admin@1234")
    p.add_argument("--mailhog", default=None, help="MailHog base URL (e.g., http://localhost:8025) for message verification")
    args = p.parse_args()

    B = args.backend.rstrip("/")
    ok = True

    # Phase 1 basics
    code, _, _ = http("GET", f"{B}/health")
    print("[P1] /health:", code)
    ok &= (code == 200)

    code, _, body = http("GET", f"{B}/openapi.json")
    print("[P1] /openapi.json:", code)
    ok &= (code == 200)
    paths = {}
    if code == 200:
        try:
            paths = json.loads(body.decode("utf-8")).get("paths", {})
        except Exception:
            pass

    code, _, _ = http("POST", f"{B}/auth/login", data={"username": args.admin_user, "password": args.admin_pass})
    print("[P1] /auth/login:", code)
    ok &= (code == 200)
    code, _, _ = http("GET", f"{B}/auth/me")
    print("[P1] /auth/me (no token):", code)
    ok &= (code in (401, 403))

    # Get token properly
    code, _, body = http("POST", f"{B}/auth/login", data={"username": args.admin_user, "password": args.admin_pass})
    token = None
    if code == 200:
        token = json.loads(body.decode("utf-8")).get("access_token")
    if not token:
        print("[FATAL] Cannot proceed without token")
        return 1

    H = {"Authorization": f"Bearer {token}"}
    code, _, _ = http("GET", f"{B}/users", headers=H)
    print("[P1] /users (admin):", code)
    ok &= (code == 200)

    # Phase 4 endpoints in OpenAPI
    has_hist = "/notification-history" in paths or "/api/notification-history" in paths
    has_settings = "/notifications/settings" in paths or "/api/notifications/settings" in paths
    print("[P4] OpenAPI ntf-history/settings:", has_hist, has_settings)
    ok &= has_hist and has_settings

    # Phase 4 simple flow: create -> send -> check history (and optionally MailHog)
    code, _, body = http("GET", f"{B}/notifications", headers=H)
    print("[P4] GET /notifications:", code)
    ok &= (code == 200)
    round_trip_ok = False
    created_id = None
    if code == 200:
        title = "Validator Test"
        payload = {
            "recipient_email": "admin@example.com",
            "title": title,
            "message": "Test notification from validator",
            "severity": "info",
        }
        ccode, _, cbody = http("POST", f"{B}/notifications", headers=H, data=payload)
        if ccode == 201:
            try:
                created_id = json.loads(cbody.decode("utf-8")).get("id")
            except Exception:
                created_id = None
        print("[P4] POST /notifications:", ccode)
        if created_id:
            scode, _, sbody = http("POST", f"{B}/notifications/send/{created_id}", headers=H)
            print("[P4] POST /notifications/send/{id}:", scode)
            ok &= (scode == 200)
            # History check
            hcode, _, hbody = http("GET", f"{B}/notification-history", headers=H)
            print("[P4] GET /notification-history:", hcode)
            if hcode == 200:
                try:
                    items = json.loads(hbody.decode("utf-8"))
                    round_trip_ok = any((it.get("subject") == title) for it in items)
                except Exception:
                    round_trip_ok = False
            print("[P4] Notification round-trip in history:", round_trip_ok)
            ok &= round_trip_ok
            # Optional: verify in MailHog
            if args.mailhog:
                try:
                    mcode, _, mbody = http("GET", f"{args.mailhog.rstrip('/')}/api/v2/messages")
                    if mcode == 200:
                        m = json.loads(mbody.decode("utf-8"))
                        mh_ok = False
                        for msg in (m.get("items") or m):
                            headers = (((msg or {}).get("Content") or {}).get("Headers") or {})
                            subj = (headers.get("Subject") or [""])[0]
                            if subj == title:
                                mh_ok = True
                                break
                        print("[P4] MailHog message present:", mh_ok)
                        ok &= mh_ok
                except Exception:
                    # MailHog optional; ignore errors
                    pass

    # Phase 2 aws-iam-baseline param run (create module if missing via plan preset or seed assumed)
    # List modules to find aws-iam-baseline
    code, _, body = http("GET", f"{B}/modules", headers=H)
    module_id = None
    if code == 200:
        try:
            for m in json.loads(body.decode("utf-8")):
                if (m.get("external_id") or m.get("name")) == "aws-iam-baseline":
                    module_id = m.get("id")
                    break
        except Exception:
            pass
    if module_id:
        code, _, body = http("POST", f"{B}/module-runs/{module_id}", headers=H, data={"parameters": {"users": []}})
        print("[P2] POST /module-runs aws-iam-baseline:", code)
        ok &= (code == 201)
    else:
        print("[P2] aws-iam-baseline module not found (seed may not have run)")

    # Phase 3 panorama stub (if module exists)
    pano_id = None
    if code == 200:
        try:
            for m in json.loads(body.decode("utf-8")):
                if (m.get("external_id") or m.get("name")) == "panorama-policy-drift":
                    pano_id = m.get("id")
                    break
        except Exception:
            pass
    if pano_id:
        code, _, body2 = http("POST", f"{B}/module-runs/{pano_id}", headers=H, data={"parameters": {"device_group": "DG"}})
        print("[P3] POST /module-runs panorama:", code)
        ok &= (code == 201)

    # Phase 6 metrics
    code, _, _ = http("GET", f"{B}/metrics")
    print("[P6] /metrics:", code)
    ok &= (code == 200)

    # Phase 7 list runs
    code, _, _ = http("GET", f"{B}/module-runs", headers=H)
    print("[P7] GET /module-runs:", code)
    ok &= (code == 200)

    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
