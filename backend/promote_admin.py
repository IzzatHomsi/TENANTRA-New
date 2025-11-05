# promote_admin.py — idempotently set a user’s role
import argparse
from app.database import SessionLocal
from app.models.user import User

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--username", default=None)
    ap.add_argument("--email", default=None)
    ap.add_argument("--role", required=True)
    args = ap.parse_args()

    if not (args.username or args.email):
        raise SystemExit("Provide --username or --email")

    s = SessionLocal()
    try:
        q = s.query(User)
        if args.username:
            q = q.filter(User.username == args.username)
        if args.email:
            q = q.filter(User.email == args.email)
        u = q.first()
        if not u:
            raise SystemExit("User not found")

        before = u.role
        u.role = args.role
        s.commit()
        print(f"[promote_admin] Updated: id={u.id}, username={u.username}, role {before} -> {u.role}")
    finally:
        s.close()

if __name__ == "__main__":
    main()
