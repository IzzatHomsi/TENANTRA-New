# backend/app/scripts/promote_admin.py
"""
Promote a user to a target role (default: admin) in the Tenantra DB.

Usage (inside container):
    python -m app.scripts.promote_admin --username admin --role admin
    # or by email:
    python -m app.scripts.promote_admin --email admin@tenantra.local --role admin

Idempotent: runs UPDATE only if a matching user exists and role differs.
Exits with code 0 on success (even if already set), >0 on error.
"""
import sys
import argparse

try:
    from app.database import SessionLocal
    from app.models.user import User
except Exception as e:
    print(f"[promote_admin] Import error: {e}", file=sys.stderr)
    sys.exit(2)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--username", help="username to update")
    ap.add_argument("--email", help="email to update")
    ap.add_argument("--role", default="admin", help="target role (default: admin)")
    args = ap.parse_args()

    if not args.username and not args.email:
        print("Provide --username or --email", file=sys.stderr)
        sys.exit(2)

    db = SessionLocal()
    try:
        q = db.query(User)
        if args.username:
            q = q.filter(User.username == args.username)
        if args.email:
            q = q.filter(User.email == args.email)
        user = q.first()
        if not user:
            print("[promote_admin] No matching user")
            return 1
        if getattr(user, "role", None) == args.role:
            print(f"[promote_admin] Already {args.role}: id={user.id}, username={user.username}")
            return 0
        user.role = args.role
        db.add(user)
        db.commit()
        print(f"[promote_admin] Updated: id={user.id}, username={user.username}, role={user.role}")
        return 0
    except Exception as e:
        db.rollback()
        print(f"[promote_admin] Error: {e}", file=sys.stderr)
        return 3
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())
