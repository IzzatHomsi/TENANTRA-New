import os
import sys

# Add /app to sys.path dynamically
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

def debug_auth():
    db = SessionLocal()
    user = db.query(User).filter(User.username == 'admin').first()
    if user:
        print(f"[DEBUG] Found user: {user.username}")
        print(f"[DEBUG] Stored hash: {user.password_hash}")
        try:
            valid = verify_password('admin123', user.password_hash)
            print(f"[DEBUG] Password check: {'MATCH' if valid else 'NO MATCH'}")
        except Exception as e:
            print(f"[ERROR] Exception during password check: {e}")
    else:
        print("[ERROR] Admin user not found in database")

if __name__ == '__main__':
    debug_auth()
