#!/usr/bin/env python3
"""
Tenantra Phases 0–8 Validator (backend + basic frontend reachability)

- Uses only Python stdlib (urllib, json) — no pip requirements.
- Prints a human-readable PASS/FAIL report with reasons.
- Verifies auth lifecycle, admin role, protected routes, dual prefixes,
  OpenAPI route presence for planned phases, basic CORS header, and SPA reachability.

Run:
  python tools/validate_tenantra_phases.py --backend http://localhost:5000 --frontend http://localhost:5173 \
         --admin-user adm --admin-pass Admin@1234 --tenant default
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from urllib.parse import urlencode

def http(method, url, headers=None, data=None, timeout=10):
    req = urllib.request.Request(url, method=method, headers=headers or {})
    if data is not None:
        if isinstance(data, (dict, list)):
            body = json.dumps(data).encode("utf-8")
            req.add_header("Content-Type", "application/json")
        elif isinstance(data, str):
            body = data.encode("utf-8")
        else:
            body = data
    else:
        body = None
    try:
        with urllib.request.urlopen(req, data=body, timeout=timeout) as resp:
            return resp.getcode(), resp.headers, resp.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read()
    except urllib.error.URLError as e:
        return 0, {}, str(e).encode("utf-8")

def expect(condition, ok_msg, fail_msg):
    return {"ok": bool(condition), "ok_msg": ok_msg if condition else None, "fail_msg": None if condition else fail_msg}

def pretty(label, result):
    status = "PASS" if result["ok"] else "FAIL"
    reason = result["ok_msg"] or result["fail_msg"] or ""
    return f"[{status}] {label}: {reason}"

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backend", required=False, default="http://localhost:5000")
    p.add_argument("--frontend", required=False, default="http://localhost:5173")
    p.add_argument("--admin-user", required=False, default="adm")
    p.add_argument("--admin-pass", required=False, default="Admin@1234")
    p.add_argument("--tenant", required=False, default="default")
    args = p.parse_args()

    B = args.backend.rstrip("/")
    F = args.frontend.rstrip("/")

    report = []

    # --- Health ---
    code, hdr, body = http("GET", f"{B}/health/ping")
    report.append(expect(code == 200, "Backend health OK", f"/health/ping => {code}"))

    # --- OpenAPI ---
    code, hdr, body = http("GET", f"{B}/openapi.json")
    openapi_ok = (code == 200)
    report.append(expect(openapi_ok, "OpenAPI available", f"/openapi.json => {code}"))
    paths = {}
    if openapi_ok:
        try:
            paths = json.loads(body.decode("utf-8")).get("paths", {})
        except Exception:
            paths = {}
            report.append(expect(False, "", "OpenAPI parse failed"))
    else:
        paths = {}

    # --- Dual routing sanity: POST /auth/login and /api/auth/login should exist (no 404) ---
    # (we expect 422 when missing body — but not 404)
    code, hdr, body = http("POST", f"{B}/auth/login")
    report.append(expect(code != 404, "POST /auth/login reachable", f"/auth/login => {code}"))
    code2, hdr2, body2 = http("POST", f"{B}/api/auth/login")
    report.append(expect(code2 != 404, "POST /api/auth/login reachable", f"/api/auth/login => {code2}"))

    # --- Login proper ---
    login_payload = {"username": args.admin_user, "password": args.admin_pass}
    code, hdr, body = http("POST", f"{B}/auth/login", data=login_payload)
    ok_login = (code == 200)
    token = None
    user = None
    if ok_login:
        try:
            j = json.loads(body.decode("utf-8"))
            token = j.get("access_token")
            user = j.get("user")
        except Exception:
            ok_login = False
    report.append(expect(ok_login and token, "Login OK (/auth/login)", f"Login failed code={code} body={body[:200]!r}"))
    if user:
        report.append(expect(True, f"Login returned user: {user.get('username','?')}", ""))

    # --- /auth/me ---
    me_ok = False
    is_admin = False
    is_active = False
    if token:
        code, hdr, body = http("GET", f"{B}/auth/me", headers={"Authorization": f"Bearer {token}"})
        me_ok = (code == 200)
        if me_ok:
            try:
                me = json.loads(body.decode("utf-8"))
                role = (me.get("role") or me.get("user", {}).get("role"))
                is_admin = (role == "admin" or role == "administrator" or (isinstance(role, dict) and role.get("name") == "admin"))
                is_active = bool(me.get("is_active", True) or me.get("user", {}).get("is_active", True))
            except Exception:
                me_ok = False
        report.append(expect(me_ok, "/auth/me OK", f"/auth/me => {code}"))
        report.append(expect(is_admin, "Role=admin", "Role not admin"))
        report.append(expect(is_active, "User is_active=True", "User is not active"))
    else:
        report.append(expect(False, "", "No token to test /auth/me"))

    # --- Protected routes security ---
    # /users (GET) should require admin; test without token (401/403) then with token (200)
    code, hdr, body = http("GET", f"{B}/users")
    report.append(expect(code in (401, 403), "GET /users unauthorized without token", f"Unexpected code without token: {code}"))
    if token:
        code, hdr, body = http("GET", f"{B}/users", headers={"Authorization": f"Bearer {token}"})
        report.append(expect(code == 200, "GET /users OK as admin", f"/users => {code}"))

    # --- CORS sanity (not exhaustive): expect Access-Control-Allow-Origin in response to OPTIONS on a typical endpoint
    code, hdr, body = http("OPTIONS", f"{B}/auth/login")
    cors_ok = ("access-control-allow-origin" in {k.lower(): v for k, v in hdr.items()})
    report.append(expect(cors_ok, "CORS header present on OPTIONS /auth/login", "Missing ACAO header"))

    # --- OpenAPI routes presence checks for planned features through Phase 8 (best-effort)
    expected_paths = [
        "/auth/login",
        "/auth/me",
        "/users",
        "/health/ping",
        # add others you’ve planned up to Phase 8 (examples):
        "/notifications",            # if present by Phase ≤8
        "/compliance/results",       # if present by Phase ≤8
        "/exports",                  # if export API added ≤8
    ]
    if paths:
        for pth in expected_paths:
            # allow either root or under /api; check both
            exists = (pth in paths) or (f"/api{pth}" in paths)
            report.append(expect(exists, f"OpenAPI has {pth} (or /api{pth})", f"Missing in OpenAPI: {pth}"))

    # --- Frontend reachability (SPA returns HTML)
    code, hdr, body = http("GET", f"{F}/")
    html_like = (code == 200 and b"<html" in body.lower())
    report.append(expect(html_like, "Frontend reachable (/) returns HTML", f"Frontend / => {code}"))

    # Note: actual in-browser redirect checks (A1–E22) require a headless browser.
    # We validate backend equivalents and surface SPA availability here.

    # --- Summary ---
    passed = sum(1 for r in report if r["ok"])
    total = len(report)
    print("\n=== Tenantra Phases 0–8 Validation Report ===")
    print(f"Target backend:  {B}")
    print(f"Target frontend: {F}")
    print(f"Admin user:      {args.admin_user}")
    print("----------------------------------------------")
    for item, res in zip(range(1, total+1), report):
        msg = res["ok_msg"] if res["ok"] else res["fail_msg"]
        status = "PASS" if res["ok"] else "FAIL"
        print(f"{item:02d}. {status} - {msg}")
    print("----------------------------------------------")
    print(f"RESULT: {passed}/{total} checks passed")
    if passed != total:
        sys.exit(1)

if __name__ == "__main__":
    main()
