#!/usr/bin/env python3
"""
Phase 0–8 Deep Audit:
- Runs entirely inside the backend container (no external deps).
- Verifies: OpenAPI, live endpoints, DB tables, Alembic heads, seed/admin state,
  and presence of required frontend components/routes through Phase 8.
- Outputs a PASS/FAIL matrix and raw evidence lines.

Environment vars (passed by PS wrapper):
  BACKEND_URL, FRONTEND_URL, ADMIN_USER, ADMIN_PASS, TENANT_NAME, FRONTEND_PATH
"""

import os, sys, json, subprocess, shlex, re
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

B = os.getenv("BACKEND_URL", "http://localhost:5000").rstrip("/")
F = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
ADMIN_USER  = os.getenv("ADMIN_USER", "adm")
ADMIN_PASS  = os.getenv("ADMIN_PASS", "Admin@1234")
TENANT_NAME = os.getenv("TENANT_NAME", "default")
FRONTEND_PATH = os.getenv("FRONTEND_PATH", "frontend")
SKIP_FE_HTTP = os.getenv("FRONTEND_SKIP_HTTP", "0").strip().lower() in {"1","true","yes","on"}
SKIP_FE_PATH = os.getenv("FRONTEND_PATH_SKIP", "0").strip().lower() in {"1","true","yes","on"}

def http(method, url, headers=None, data=None, timeout=10):
    req = Request(url, method=method, headers=headers or {})
    try:
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
        with urlopen(req, data=body, timeout=timeout) as resp:
            return resp.getcode(), dict(resp.headers), resp.read()
    except HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except URLError as e:
        return 0, {}, str(e).encode("utf-8")

def sh(cmd):
    # run in backend container shell context (we are already inside container)
    p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout

def header(title):
    print("\n=== " + title + " ===")

def passfail(ok, okmsg, failmsg):
    print(f"[{'PASS' if ok else 'FAIL'}] {okmsg if ok else failmsg}")

def main():
    # 1) Health & OpenAPI
    header("Backend health & OpenAPI")
    code, hdr, body = http("GET", f"{B}/health/ping")
    passfail(code == 200, "Backend /health/ping OK", f"/health/ping => {code}")

    code, hdr, body = http("GET", f"{B}/openapi.json")
    api_ok = (code == 200)
    passfail(api_ok, "OpenAPI available", f"/openapi.json => {code}")
    paths = {}
    if api_ok:
        try:
            paths = json.loads(body.decode("utf-8")).get("paths", {})
        except Exception as e:
            passfail(False, "", f"OpenAPI parse error: {e}")

    # 2) Critical endpoints present?
    header("Endpoint presence (root and /api)")
    def _norm(p: str) -> str:
        return p if not p.endswith('/') else p[:-1]
    def exists(p):
        p = _norm(p)
        return (p in {_norm(k) for k in paths.keys()}) or ("/api"+p in {_norm(k) for k in paths.keys()})
    for p in ["/auth/login", "/auth/me", "/health/ping", "/users"]:
        passfail(exists(p), f"OpenAPI has {p} (or /api{p})", f"Missing {p} in OpenAPI")

    # Phase 5-8 endpoints (strict)
    strict_routes = [
        "/notifications",
        "/compliance/results",
        "/exports",
        "/schedules",
        "/modules",
        "/visibility/network",
        "/visibility/files",
        "/assets",  # strict gating
        "/notification-history",  # strict gating
        "/notifications/settings",  # strict gating
    ]
    for p in strict_routes:
        passfail(exists(p), f"OpenAPI has {p}", f"Missing {p} in OpenAPI")

    # 3) Dual mount 404 check (we expect 422 for POST without body, not 404)
    header("Dual mount reachability")
    for u in [f"{B}/auth/login", f"{B}/api/auth/login"]:
        code,_,_ = http("POST", u)
        passfail(code != 404, f"{u} reachable (not 404)", f"{u} => 404 (not mounted)")

    # 4) Login and admin role/active
    header("Auth lifecycle")
    form = f"username={ADMIN_USER}&password={ADMIN_PASS}"
    code, hdr, body = http("POST", f"{B}/auth/login", headers={"Content-Type":"application/x-www-form-urlencoded"}, data=form)
    ok_login = (code == 200)
    token = None
    if ok_login:
        try:
            j = json.loads(body.decode("utf-8"))
            token = j.get("access_token")
        except Exception:
            ok_login = False
    passfail(ok_login and token, "Login accepted, token issued", f"Login failed => {code} {body[:180]!r}")
    if token:
        code,_,mebody = http("GET", f"{B}/auth/me", headers={"Authorization": f"Bearer {token}"})
        ok_me = (code == 200)
        role_ok, active_ok = False, False
        if ok_me:
            try:
                me = json.loads(mebody.decode("utf-8"))
                role = me.get("role") or (me.get("user",{}) or {}).get("role")
                is_active = me.get("is_active", True) if "is_active" in me else (me.get("user", {}).get("is_active", True))
                role_ok = (role in ("admin","administrator")) or (isinstance(role, dict) and role.get("name") == "admin")
                active_ok = bool(is_active)
            except Exception as e:
                ok_me = False
        passfail(ok_me, "/auth/me returns user", f"/auth/me => {code}")
        passfail(role_ok, "User role is admin", "Role not admin (or not returned)")
        passfail(active_ok, "User is_active=True", "User is not active")

    # 5) Protected routes behavior
    header("Protected routes (admin required)")
    code,_,_ = http("GET", f"{B}/users")
    passfail(code in (401,403), "GET /users blocked without token", f"/users without token => {code}")
    if token:
        code,_,_ = http("GET", f"{B}/users", headers={"Authorization": f"Bearer {token}"})
        passfail(code == 200, "GET /users OK with admin token", f"/users with token => {code}")

    # 6) DB presence checks (tables)
    header("Database: Alembic heads & tables")
    rc, out = sh("alembic heads")
    passfail(rc == 0, "Alembic heads listed", f"alembic heads failed: {out.strip()}")
    print(out.strip())

    # Expected tables (Phase 0–8 superset; mark what’s missing)
    expected_tables = [
        "users","tenants","modules","tenant_modules",
        "scheduled_scans","compliance_results","notifications","notification_settings",
        "refresh_tokens","audit_logs","roles","tenant_cors_origins","assets"
    ]
    rc, tbl = sh("python - << 'PY'\nfrom sqlalchemy import create_engine, inspect\nimport os, sys\nurl=os.getenv('DATABASE_URL') or os.getenv('DB_URL')\nif not url:\n    print('ERROR: DATABASE_URL or DB_URL env var not set', file=sys.stderr)\n    sys.exit(2)\nengine=create_engine(url)\nins=inspect(engine)\nprint('\\n'.join(sorted(ins.get_table_names())))\nPY")
    if rc != 0:
        passfail(False, "", f"table list failed: {tbl.strip()}")
        tables = []
    else:
        tables = [t.strip() for t in tbl.splitlines() if t.strip()]
        passfail(True, "Fetched table list", "")
        print("Tables:", ", ".join(sorted(tables)))

    for t in expected_tables:
        present = t in tables
        passfail(present, f"Table '{t}' present", f"Missing table '{t}'")

    # 7) Seed/admin sanity
    header("Seed sanity")
    rc, q = sh("python - << 'PY'\nfrom sqlalchemy import create_engine, text\nimport os, sys\nurl=os.getenv('DATABASE_URL') or os.getenv('DB_URL')\nif not url:\n    print('ERROR: DATABASE_URL or DB_URL env var not set', file=sys.stderr)\n    sys.exit(2)\nengine=create_engine(url)\nwith engine.connect() as c:\n r=c.execute(text(\"select username,is_active from users order by id limit 10\"))\n for row in r:\n  print(f\"user={row[0]} active={row[1]}\")\nPY")
    passfail(rc==0, "Listed first users", f"user list failed: {q.strip()}")
    print(q.strip())

    # 8) Frontend reachability & components presence (static tree check)
    header("Frontend reachability")
    if SKIP_FE_HTTP:
        passfail(True, "Skipped by config (FRONTEND_SKIP_HTTP)", "")
    else:
        code,_,body = http("GET", f"{F}/")
        ok_html = (code==200 and b"<html" in body.lower())
        passfail(ok_html, "Frontend (/) returns HTML", f"frontend / => {code}")

    header("Frontend source tree checks")
    if SKIP_FE_PATH:
        passfail(True, "Skipped by config (FRONTEND_PATH_SKIP)", "")
    else:
        # Check for component files that should exist by Phase 8
        component_globs = [
            "src/pages/Users.jsx",
            "src/pages/Profile.jsx",
            "src/pages/ComplianceTrends.jsx",
            "src/pages/Notifications.jsx",
            "src/pages/Schedules.jsx",
            "src/pages/Modules.jsx",
            "src/pages/Assets.jsx",
            "src/pages/NetworkExposure.jsx",
            "src/pages/FileVisibility.jsx",
            "src/components/AlertSettings.jsx"
        ]
        for g in component_globs:
            rc, out = sh(f"bash -lc 'test -f {shlex.quote(FRONTEND_PATH)}/{shlex.quote(g)} && echo OK || echo MISSING'")
            passfail(out.strip()=="OK", f"Frontend file present: {g}", f"Missing front file: {g}")

        # Check for routing file with protected routes (React Router v6+)
        route_files = ["src/App.jsx","src/routes.jsx","src/router.jsx"]
        found_route_file = False
        for rf in route_files:
            rc, out = sh(f"bash -lc 'test -f {shlex.quote(FRONTEND_PATH)}/{shlex.quote(rf)} && echo OK || echo MISSING'")
            if out.strip()=="OK":
                found_route_file = True
                passfail(True, f"Routing file present: {rf}", "")
                # quick grep of likely routes
                rc2, content = sh(f"bash -lc 'cat {shlex.quote(FRONTEND_PATH)}/{shlex.quote(rf)}'")
                for route in ["/users","/profile","/notifications","/compliance","/schedules","/modules","/assets","/network","/files"]:
                    present = (route in content)
                    passfail(present, f"Route string appears: {route}", f"Route missing: {route}")
                break
        if not found_route_file:
            passfail(False, "", "No routing file (App.jsx/routes.jsx/router.jsx) found to inspect")

    print("\n--- End of Deep Audit ---")

if __name__ == "__main__":
    main()
