"""
Seed script: creates the default admin user.
Run with: python seed.py

Credentials are read from environment variables:
  SEED_ADMIN_USERNAME  (default: admin)
  SEED_ADMIN_EMAIL     (default: admin@pipingqc.local)
  SEED_ADMIN_PASSWORD  (required — no default)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


def seed():
    admin_username = os.environ.get("SEED_ADMIN_USERNAME", "admin")
    admin_email = os.environ.get("SEED_ADMIN_EMAIL", "admin@pipingqc.local")
    admin_password = os.environ.get("SEED_ADMIN_PASSWORD")

    if not admin_password:
        print(
            "ERROR: SEED_ADMIN_PASSWORD environment variable is required.",
            file=sys.stderr,
        )
        sys.exit(1)

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == admin_username).first()
        if existing:
            print(f"User '{admin_username}' already exists — skipping.")
            return

        admin = User(
            username=admin_username,
            email=admin_email,
            hashed_password=hash_password(admin_password),
            role=UserRole.admin,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"Admin user created: username={admin_username}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
