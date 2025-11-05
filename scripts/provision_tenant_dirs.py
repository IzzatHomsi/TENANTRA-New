# provision_tenant_dirs.py — one-off tenant folder provisioning
import argparse
from app.core.tenants import ensure_tenant_roots

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--tenant", required=True, help="Tenant slug or id (e.g., acme)")
    args = p.parse_args()
    created = ensure_tenant_roots(args.tenant)
    print("Ensured paths:")
    for c in created:
        print(c)
