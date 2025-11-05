#!/usr/bin/env python3
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.tenant import Tenant
from app.models.user import User
from werkzeug.security import generate_password_hash

DATABASE_URL = os.getenv("DB_URL", "postgresql://tenantra:changeme@db/tenantra")

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def seed_data():
    # Create default tenant
    default_tenant = Tenant(name="Default Tenant")
    session.add(default_tenant)
    session.commit()

    # Create default admin user
    admin_user = User(
        username="admin",
        password_hash=generate_password_hash("admin123"),
        tenant_id=default_tenant.id
    )
    session.add(admin_user)
    session.commit()
    print("Database seeding complete: Admin user created with username 'admin' and password 'admin123'")

if __name__ == "__main__":
    seed_data()
