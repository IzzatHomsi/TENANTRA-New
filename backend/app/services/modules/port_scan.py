from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import ipaddress
import ssl
import base64
import re

from app.services.module_runner import ModuleContext, ModuleRunner, build_result
from app.database import SessionLocal
from app.models.app_setting import AppSetting


@dataclass
class PortTarget:
    host: str
    ports: List[int]


def _parse_targets(parameters: Dict[str, object]) -> List[PortTarget]:
    # Accept either a list of {host, ports[]} or a single host with ports
    targets: List[PortTarget] = []
    if isinstance(parameters.get("targets"), list):
        for item in parameters["targets"]:  # type: ignore[index]
            if isinstance(item, dict):
                host = str(item.get("host") or "").strip()
                ports = item.get("ports") or []
                if host and isinstance(ports, list):
                    ports_int = []
                    for p in ports:
                        try:
                            ports_int.append(int(p))
                        except (ValueError, TypeError):
                            pass
                    if ports_int:
                        # Expand CIDR ranges into a small sample to avoid huge scans
                        if "/" in host:
                            try:
                                net = ipaddress.ip_network(host, strict=False)
                                count = 0
                                for ip in net.hosts():
                                    targets.append(PortTarget(host=str(ip), ports=ports_int))
                                    count += 1
                                    if count >= 8:
                                        break
                            except Exception:
                                # Fallback to literal host if parsing fails
                                targets.append(PortTarget(host=host, ports=ports_int))
                        else:
                            targets.append(PortTarget(host=host, ports=ports_int))
    else:
        host = str(parameters.get("host") or "").strip()
        ports = parameters.get("ports") or [22, 80, 443]
        if host and isinstance(ports, list):
            ports_int = []
            for p in ports:
                try:
                    ports_int.append(int(p))
                except (ValueError, TypeError):
                    pass
            if ports_int:
                if "/" in host:
                    try:
                        net = ipaddress.ip_network(host, strict=False)
                        count = 0
                        for ip in net.hosts():
                            targets.append(PortTarget(host=str(ip), ports=ports_int))
                            count += 1
                            if count >= 8:
                                break
                    except Exception:
                        targets.append(PortTarget(host=host, ports=ports_int))
                else:
                    targets.append(PortTarget(host=host, ports=ports_int))
    return targets


def _load_default_targets(tenant_id: Optional[int]) -> List[PortTarget]:
    session = SessionLocal()
    try:
        keys = ["networking.plan.targets"]
        rows = (
            session.query(AppSetting)
            .filter(
                (AppSetting.tenant_id == tenant_id) | (AppSetting.tenant_id.is_(None)),
                AppSetting.key.in_(keys),
            )
            .all()
        )
        # prefer tenant-specific, fallback to global
        value = None
        for r in rows:
            if r.tenant_id == tenant_id and r.key == "networking.plan.targets":
                value = r.value
                break
        if value is None:
            for r in rows:
                if r.tenant_id is None and r.key == "networking.plan.targets":
                    value = r.value
                    break
        targets: List[PortTarget] = []
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    host = str(item.get("host") or "").strip()
                    ports = item.get("ports") or []
                    if host and isinstance(ports, list):
                        ports_int = []
                        for p in ports:
                            try:
                                ports_int.append(int(p))
                            except (ValueError, TypeError):
                                pass
                        if ports_int:
                            targets.append(PortTarget(host=host, ports=ports_int))
        return targets
    finally:
        session.close()


class PortScanModule(ModuleRunner):
    name = "Networking — Port Scan"
    slug = "port-scan"
    parameter_schema = {
        "type": "object",
        "properties": {
            "host": {"type": "string"},
            "ports": {
                "type": "array",
                "items": {"type": "integer"},
                "default": [22, 80, 443],
            },
            "targets": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "host": {"type": "string"},
                        "ports": {"type": "array", "items": {"type": "integer"}},
                    },
                    "required": ["host"],
                },
            },
            "timeout_ms": {"type": "integer", "default": 800},
            "capture_banner": {"type": "boolean", "default": True},
            "tls_probe": {"type": "boolean", "default": True},
        },
    }

    def run(self, context: ModuleContext):  # type: ignore[override]
        params: Dict[str, object] = context.parameters or {}
        timeout_ms = int(params.get("timeout_ms") or 800)
        sock_timeout = max(0.1, timeout_ms / 1000.0)
        capture_banner = bool(params.get("capture_banner") if params.get("capture_banner") is not None else True)
        tls_probe = bool(params.get("tls_probe") if params.get("tls_probe") is not None else True)
        targets = _parse_targets(params)
        if not targets:
            targets = _load_default_targets(getattr(context, "tenant_id", None))
        findings: List[Dict[str, object]] = []
        for t in targets:
            for port in t.ports:
                status: str
                banner: Optional[str] = None
                tls: Optional[Dict[str, object]] = None
                http_info: Optional[Dict[str, object]] = None
                software: Optional[List[Dict[str, str]]] = None
                try:
                    with socket.create_connection((t.host, port), timeout=sock_timeout) as s:
                        status = "open"
                        s.settimeout(sock_timeout)
                        if capture_banner:
                            try:
                                # Heuristics: send minimal probe for common services
                                probe_sent = False
                                if port in (80, 8080, 8000, 8888):
                                    # Prefer GET to capture headers (e.g., Server)
                                    s.sendall(b"GET / HTTP/1.0\r\nHost: \r\nUser-Agent: TenantraPortScan/1.0\r\n\r\n")
                                    probe_sent = True
                                elif port in (22,):
                                    # SSH usually sends banner first; just read
                                    probe_sent = False
                                elif port in (25, 110, 143, 21, 119):
                                    # SMTP/POP3/IMAP/FTP/NNTP read greeting
                                    probe_sent = False
                                if not probe_sent:
                                    try:
                                        s.sendall(b"\r\n")
                                    except Exception:
                                        pass
                                data = s.recv(2048)
                                if data:
                                    banner = data.decode("utf-8", errors="ignore").strip()
                                    # Parse HTTP structure (status line + headers) if applicable
                                    if port in (80, 8080, 8000, 8888):
                                        http_info = _parse_http_info(data)
                                    # Extract FTP/NNTP software versions if applicable
                                    if port == 21:
                                        software = _extract_software_versions(banner, service_hint="ftp")
                                    elif port == 119:
                                        software = _extract_software_versions(banner, service_hint="nntp")
                            except Exception:
                                banner = None
                        # Helper to extract TLS info from a wrapped socket
                        def _extract_tls_info(sock: ssl.SSLSocket, server_name: str) -> Dict[str, object]:
                            cert_dict = sock.getpeercert() or {}
                            cert_bin = sock.getpeercert(binary_form=True)
                            not_after = cert_dict.get('notAfter')
                            issuer = cert_dict.get('issuer')
                            from datetime import datetime
                            expires_in_days = None
                            if isinstance(not_after, str):
                                try:
                                    expires = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                                    expires_in_days = (expires - datetime.utcnow()).days
                                except Exception:
                                    expires_in_days = None
                            return {
                                "protocol": sock.version(),
                                "alpn": sock.selected_alpn_protocol(),
                                "sni": server_name,
                                "certificate": cert_dict,
                                "certificate_der_b64": base64.b64encode(cert_bin).decode("ascii") if cert_bin else None,
                                "not_after": not_after,
                                "issuer": issuer,
                                "expires_in_days": expires_in_days,
                            }

                        # STARTTLS upgrades for text protocols
                        if tls_probe and port in (25, 110, 143):
                            try:
                                if port == 25:  # SMTP
                                    try:
                                        s.sendall(b"EHLO tenantra.local\r\n")
                                        _ = s.recv(1024)
                                    except Exception:
                                        pass
                                    s.sendall(b"STARTTLS\r\n")
                                    resp = s.recv(1024)
                                    if resp and resp.startswith(b"220"):
                                        ctx = ssl.create_default_context()
                                        with ctx.wrap_socket(s, server_hostname=t.host) as ssock:
                                            tls = _extract_tls_info(ssock, t.host)
                                elif port == 110:  # POP3
                                    s.sendall(b"STLS\r\n")
                                    resp = s.recv(1024)
                                    if resp and resp.upper().startswith(b"+OK"):
                                        ctx = ssl.create_default_context()
                                        with ctx.wrap_socket(s, server_hostname=t.host) as ssock:
                                            tls = _extract_tls_info(ssock, t.host)
                                elif port == 143:  # IMAP
                                    s.sendall(b"a001 STARTTLS\r\n")
                                    resp = s.recv(1024)
                                    if resp and b"OK" in resp.upper():
                                        ctx = ssl.create_default_context()
                                        with ctx.wrap_socket(s, server_hostname=t.host) as ssock:
                                            tls = _extract_tls_info(ssock, t.host)
                            except Exception:
                                pass

                        if tls_probe and port in (443, 8443, 9443):
                            try:
                                ctx = ssl.create_default_context()
                                with ctx.wrap_socket(s, server_hostname=t.host) as ssock:
                                    tls = _extract_tls_info(ssock, t.host)
                            except Exception:
                                # attempt a second handshake from a new socket to avoid corrupted state
                                try:
                                    with socket.create_connection((t.host, port), timeout=sock_timeout) as s2:
                                        ctx = ssl.create_default_context()
                                        with ctx.wrap_socket(s2, server_hostname=t.host) as ssock2:
                                            tls = _extract_tls_info(ssock2, t.host)
                                except Exception:
                                    tls = None
                except Exception:
                    status = "closed"
                entry: Dict[str, object] = {"host": t.host, "port": port, "status": status}
                if banner:
                    entry["banner"] = banner
                if tls is not None:
                    entry["tls"] = tls
                if http_info is not None:
                    entry["http"] = http_info
                if software:
                    entry["software"] = software
                findings.append(entry)

        details = {
            "targets": [t.__dict__ for t in targets],
            "findings": findings,
        }
        status = "success"
        return build_result(status=status, details=details)


def _parse_http_info(raw: bytes) -> Dict[str, object]:
    try:
        text = raw.decode("iso-8859-1", errors="ignore")  # headers are latin-1 safe
        head = text.split("\r\n\r\n", 1)[0]
        lines = head.split("\r\n")
        if not lines:
            return {}
        status_line = lines[0]
        status_code: Optional[int] = None
        reason: Optional[str] = None
        if status_line.startswith("HTTP/"):
            parts = status_line.split(" ", 2)
            if len(parts) >= 2 and parts[1].isdigit():
                status_code = int(parts[1])
                reason = parts[2] if len(parts) >= 3 else None
        headers_lower: Dict[str, str] = {}
        set_cookie_count = 0
        for line in lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers_lower[k.strip().lower()] = v.strip()
                if k.strip().lower() == "set-cookie":
                    set_cookie_count += 1
        return {
            "status_code": status_code,
            "reason": reason,
            "server": headers_lower.get("server"),
            "date": headers_lower.get("date"),
            "content_type": headers_lower.get("content-type"),
            "location": headers_lower.get("location"),
            "connection": headers_lower.get("connection"),
            "content_length": headers_lower.get("content-length"),
            "cache_control": headers_lower.get("cache-control"),
            "set_cookie_count": set_cookie_count,
        }
    except Exception:
        return {}


_KNOWN_PRODUCTS = (
    # FTP
    "vsFTPd", "ProFTPD", "Pure-FTPd", "FileZilla", "FileZilla Server", "Microsoft FTP Service", "wu-ftpd",
    "Serv-U", "Gene6-FTPD", "WS_FTP", "TitanFTP", "CerberusFTPServer",
    # NNTP
    "INN", "InterNetNews", "Cyclone", "DNews", "Leafnode", "Hamster", "sn", "diablo",
)


def _extract_software_versions(banner: str, service_hint: str) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    if not banner:
        return out
    try:
        # Look for tokens like "Product 1.2.3" or "Product/1.2.3"
        pattern = re.compile(r"([A-Za-z][A-Za-z0-9._-]{1,50})[ /]([0-9]+\.[0-9.]+)")
        for m in pattern.finditer(banner):
            product, version = m.group(1), m.group(2)
            if product in _KNOWN_PRODUCTS or service_hint in ("ftp", "nntp"):
                out.append({"product": product, "version": version})
        # Special cases without explicit numeric versions
        if "Microsoft FTP Service" in banner and not any(s["product"].startswith("Microsoft FTP Service") for s in out):
            out.append({"product": "Microsoft FTP Service", "version": "unknown"})
        if service_hint == "nntp" and ("InterNetNews" in banner or "INN" in banner) and not any(s["product"].lower().startswith("inn") for s in out):
            out.append({"product": "INN", "version": "unknown"})
    except Exception:
        return out
    return out
