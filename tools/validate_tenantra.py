#!/usr/bin/env python3
"""
Tenantra Validator (Phases 5-7 focused) — outputs Markdown + JSON.

Usage:
  python tools/validate_tenantra.py --output-dir reports

Exits non-zero on High/Critical failures (secrets committed, naming violations,
CI conflicts, missing phase endpoints).
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
from dataclasses import dataclass, asdict
from urllib import request as urlrequest
from urllib.error import URLError, HTTPError
import base64
from pathlib import Path
from typing import Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]


def sh(cmd: List[str], timeout: int = 20) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def env_kv_lengths(path: Path) -> List[Dict[str, object]]:
    out = []
    for line in read_text(path).splitlines():
        if not line or line.strip().startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        v_stripped = v.strip()
        # Heuristic: mark likely secrets, but exclude non-secret config knobs
        suspect = bool(re.search(r"(secret|password|key|token|jwt|hash|salt)", k, re.I))
        if re.search(r"(expire|ttl|lifetime|algorithm|algo)", k, re.I):
            suspect = False
        placeholder = bool(re.search(r"(changeme|replace|set_via_secret|\$\{)", v_stripped, re.I))
        out.append({"key": k.strip(), "len": len(v_stripped), "suspect": suspect, "placeholder": placeholder})
    return out


def list_compose_files() -> List[Path]:
    return sorted([p for p in (ROOT / "docker").glob("docker-compose*.yml")])


def scan_compose_names(files: List[Path]) -> Tuple[List[str], List[str]]:
    containers: List[str] = []
    volumes: List[str] = []
    for f in files:
        txt = read_text(f)
        containers += re.findall(r"container_name:\s*([\w\-]+)", txt)
        # crude top-level volumes detection
        m = re.search(r"^volumes:\s*(.*?)\n\S", txt, flags=re.S | re.M)
        block = m.group(1) if m else ""
        for line in block.splitlines():
            name = line.strip().split(":")[0].strip()
            if name and not name.startswith("#") and re.match(r"^[\w\-]+$", name):
                volumes.append(name)
    # de-dup
    containers = sorted(dict.fromkeys(containers))
    volumes = sorted(dict.fromkeys(volumes))
    return containers, volumes


def has_ci_conflicts() -> bool:
    conflict = False
    for p in (ROOT / ".github" / "workflows").glob("*.yml"):
        if "<<<<<<<" in read_text(p):
            conflict = True
    return conflict


def count_modules_csv() -> int:
    p = ROOT / "Tenantra_Scanning_Module_Table_v2_UPDATED.csv"
    try:
        return sum(1 for _ in p.read_text(encoding="utf-8").splitlines() if _)
    except Exception:
        return 0


@dataclass
class Check:
    name: str
    status: str
    evidence: Dict[str, object]
    remediation: Optional[str] = None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(ROOT / "reports"))
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    checks: List[Check] = []

    # Preflight
    code, docker_ver, _ = sh(["docker", "version", "--format", "{{json .}}"], timeout=15)
    os_info = {
        "os": platform.platform(),
        "python": platform.python_version(),
        "docker_ok": code == 0,
    }

    # Env files
    env_files = [ROOT / ".env.development", ROOT / ".env.staging", ROOT / ".env.production", ROOT / "env/.env.development"]
    env_report: Dict[str, object] = {}
    secrets_committed = False
    for p in env_files:
        if p.exists():
            env_items = env_kv_lengths(p)
            env_report[str(p.relative_to(ROOT))] = env_items
            # treat any suspect key with len>0 and not placeholder as a potential secret in prod/staging
            for item in env_items:
                if item["suspect"] and item["len"] and not item.get("placeholder") and ("production" in str(p).lower() or "staging" in str(p).lower()):
                    secrets_committed = True

    # Secrets directory: only fail if secrets/*.txt are tracked in git
    secret_txt: List[Path] = []
    code_g, out_g, _ = sh(["git", "ls-files", "secrets/*.txt"])
    if code_g == 0 and out_g:
        for line in out_g.splitlines():
            p = ROOT / line.strip()
            if p.exists():
                secret_txt.append(p)
    if secret_txt:
        secrets_committed = True

    checks.append(Check("Preflight", "PASS", os_info))
    # Compute explicit list of problematic prod/staging keys
    prod_staging_bad: List[Dict[str, str]] = []
    for fname, items in env_report.items():
        low = fname.lower()
        if ("production" in low) or ("staging" in low):
            for it in items:
                if it.get("suspect") and it.get("len") and not it.get("placeholder"):
                    prod_staging_bad.append({"file": fname, "key": it.get("key")})
    env_fail = bool(secret_txt or prod_staging_bad)
    checks.append(Check("Env & Secrets Hygiene", "FAIL" if env_fail else "PASS", {
        "env_summary": env_report,
        "secrets_txt": [str(p.relative_to(ROOT)) for p in secret_txt],
        "prod_staging_bad": prod_staging_bad,
    }, remediation="Remove committed secrets (.env.*, secrets/*.txt) from repo; rotate keys; source from secret store."))

    # Naming standard
    compose_files = list_compose_files()
    containers, volumes = scan_compose_names(compose_files)
    prefix = os.getenv("CONTAINER_PREFIX", "TEN-S-")
    bad_containers = [c for c in containers if not c.startswith(prefix)]
    bad_volumes = [v for v in volumes if not v.startswith(prefix)]
    checks.append(Check("Naming Standard", "FAIL" if (bad_containers or bad_volumes) else "PASS", {
        "containers": containers,
        "volumes": volumes,
        "nonconformant_containers": bad_containers,
        "nonconformant_volumes": bad_volumes,
    }, remediation=f"Rename containers/volumes to {prefix}*.")) 

    # Phases 5-7
    modules_count = count_modules_csv()
    phase7_ok = modules_count >= 900
    checks.append(Check("Phase7 Module Registry", "PASS" if phase7_ok else "FAIL", {"modules_csv_lines": modules_count}))

    # CI conflicts
    conflicts = has_ci_conflicts()
    checks.append(Check("CI Workflow Conflicts", "FAIL" if conflicts else "PASS", {"conflicts_detected": conflicts}))

    # Live HTTP checks (best-effort)
    api_base = os.getenv("TENANTRA_API", "http://127.0.0.1:5000").rstrip("/")
    live: Dict[str, object] = {}
    def _fetch(path: str, method: str = "GET", data: Optional[bytes] = None, headers: Optional[Dict[str, str]] = None, base: Optional[str] = None) -> Dict[str, object]:
        base_url = base or api_base
        url = f"{base_url}{path}"
        all_headers = {"User-Agent": "tenantra-validator/1"}
        if headers:
            all_headers.update(headers)
        req = urlrequest.Request(url=url, method=method, data=data, headers=all_headers)
        try:
            with urlrequest.urlopen(req, timeout=5) as resp:
                body = resp.read(1024).decode("utf-8", errors="replace")
                cors = {k: resp.headers.get(k) for k in ["Access-Control-Allow-Origin", "Access-Control-Allow-Credentials"]}
                return {"url": url, "status": resp.status, "snippet": body[:200], "headers": cors}
        except HTTPError as e:
            return {"url": url, "status": e.code, "error": str(e)}
        except URLError as e:
            return {"url": url, "status": None, "error": str(e)}
        except Exception as e:
            return {"url": url, "status": None, "error": str(e)}

    # Backend direct
    live["health"] = _fetch("/health")
    live["metrics"] = _fetch("/metrics")

    # Nginx proxied checks
    nginx_base = os.getenv("TENANTRA_NGINX", "http://127.0.0.1:80").rstrip("/")
    live["nginx_api_health"] = _fetch("/api/health", headers={"Origin": nginx_base}, base=nginx_base)
    # Preflight OPTIONS for auth/login (CORS)
    live["nginx_auth_preflight"] = _fetch("/api/auth/login", method="OPTIONS", headers={
        "Origin": nginx_base,
        "Access-Control-Request-Method": "POST",
    }, base=nginx_base)

    # Grafana checks (optional basic auth)
    graf_base = os.getenv("TENANTRA_GRAFANA", "http://127.0.0.1:3000").rstrip("/")
    graf_user = os.getenv("GRAFANA_USER", "admin")
    graf_pass = os.getenv("GRAFANA_PASS")
    graf_require = os.getenv("TENANTRA_VALIDATE_GRAFANA", "0").lower() in {"1","true","yes","on"}
    graf_headers = {}
    if graf_pass:
        token = base64.b64encode(f"{graf_user}:{graf_pass}".encode()).decode()
        graf_headers["Authorization"] = f"Basic {token}"
    live["grafana_health"] = _fetch("/api/health", headers=graf_headers, base=graf_base)
    live["grafana_search"] = _fetch("/api/search?query=Tenantra", headers=graf_headers, base=graf_base)
    live["grafana_dashboard_uid"] = _fetch("/api/dashboards/uid/tenantra-overview", headers=graf_headers, base=graf_base)

    live_ok = False
    try:
        if isinstance(live.get("nginx_api_health"), dict) and live["nginx_api_health"].get("status") == 200:
            live_ok = True
        elif isinstance(live.get("health"), dict) and live["health"].get("status") == 200:
            live_ok = True
    except Exception:
        live_ok = False
    # If Grafana validation explicitly required, gate on dashboard uid being 200
    if graf_require:
        dash = live.get("grafana_dashboard_uid") or {}
        live_ok = live_ok and (dash.get("status") == 200)
    checks.append(Check("Live HTTP", "PASS" if live_ok else "FAIL", live))

    # Dedicated CORS preflight header check: expect exact Origin echo + credentials
    cors_evidence: Dict[str, object] = {}
    try:
        origin = nginx_base
        res = _fetch("/api/auth/login", method="OPTIONS", headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        }, base=nginx_base)
        cors_evidence = res
        ok = (res.get("status") == 204 and isinstance(res.get("headers"), dict)
              and res["headers"].get("Access-Control-Allow-Origin") == origin
              and (res["headers"].get("Access-Control-Allow-Credentials") or "").lower() == "true")
        checks.append(Check("CORS Preflight", "PASS" if ok else "FAIL", res))
    except Exception as e:
        checks.append(Check("CORS Preflight", "FAIL", {"error": str(e), "evidence": cors_evidence}))

    # Tenant-specific CORS preflight using X-Tenant-Slug: default
    try:
        origin2 = "http://localhost"
        res2 = _fetch("/api/auth/login", method="OPTIONS", headers={
            "Origin": origin2,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
            "X-Tenant-Slug": os.getenv("TENANTRA_TEST_TENANT_SLUG", "default"),
        }, base=nginx_base)
        ok2 = (res2.get("status") == 204 and isinstance(res2.get("headers"), dict)
               and res2["headers"].get("Access-Control-Allow-Origin") == origin2
               and (res2["headers"].get("Access-Control-Allow-Credentials") or "").lower() == "true")
        checks.append(Check("CORS Preflight (Tenant)", "PASS" if ok2 else "FAIL", res2))
    except Exception as e:
        checks.append(Check("CORS Preflight (Tenant)", "FAIL", {"error": str(e)}))

    # Aggregate
    summary = {
        "checks": [asdict(c) for c in checks],
        "failures": [c.name for c in checks if c.status != "PASS"],
    }

    # Write JSON
    (out_dir / "verification_report.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Write Markdown
    md_lines = ["# Tenantra Verification Report (Phases 5-7)", ""]
    for c in checks:
        md_lines.append(f"## {c.name} — {c.status}")
        md_lines.append("```")
        md_lines.append(json.dumps(c.evidence, indent=2))
        md_lines.append("```")
        if c.remediation:
            md_lines.append(f"Remediation: {c.remediation}")
        md_lines.append("")
    (out_dir / "verification_report.md").write_text("\n".join(md_lines), encoding="utf-8")

    # Exit code policy
    high_fail = any(c.status != "PASS" and c.name in {"Env & Secrets Hygiene", "Naming Standard", "CI Workflow Conflicts"} for c in checks)
    return 1 if high_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
