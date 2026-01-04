#!/usr/bin/env python3
"""
Script to create an admin user for Python Era
Usage: python create_admin.py
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import SessionLocal, User, hash_password

def create_admin():
    db = SessionLocal()
    try:
        username = input("Enter admin username: ").strip()
        email = input("Enter admin email: ").strip()
        password = input("Enter admin password: ").strip()
        
        if not username or not email or not password:
            print("Error: All fields are required")
            return
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                print(f"Error: Username '{username}' already exists")
            else:
                print(f"Error: Email '{email}' already exists")
            return
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_admin=True
        )
        db.add(admin)
        db.commit()
        
        print(f"\n✓ Admin user '{username}' created successfully!")
        print(f"  Email: {email}")
        print(f"  Admin: True")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

