"""
Seed script: creates the default admin user.
Run with: python seed.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password


def seed():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == "admin").first()
        if existing:
            print("Admin user already exists — skipping.")
            return

        admin = User(
            username="admin",
            email="admin@pipingqc.local",
            hashed_password=hash_password("admin123"),
            role=UserRole.admin,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print("Admin user created: username=admin password=admin123")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
