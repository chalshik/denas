#!/usr/bin/env python3
"""
Quick script to create a default superadmin user.

This is a simplified version that creates a superadmin with default credentials.
Use this for quick setup during development.

Usage:
    python scripts/quick_superadmin.py
"""

import asyncio
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User, UserType
from app.services.firebase_service import FirebaseService
from firebase_admin import auth
import firebase_admin
from firebase_admin import credentials
import os
import time

# Default superadmin credentials (change these!)
DEFAULT_ADMIN = {
    "email": "admin@cistech.kg",
    "password": "Admin123!",
    "first_name": "Cis",
    "last_name": "Admin",
    "phone": "+996500123456",
    "user_type": UserType.SUPERADMIN,
    "claims": {
        "user_type": "SUPERADMIN",
        "admin": True,
        "super_admin": True,
        # Granular permissions
        "can_manage_users": True,
        "can_manage_vendors": True,
        "can_manage_products": True,
        "can_view_analytics": True,
        "can_manage_settings": True
    }
}

def initialize_firebase_admin():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase app is already initialized
        firebase_admin.get_app()
        print("✅ Firebase Admin already initialized")
        return True
    except ValueError:
        # Initialize Firebase app
        try:
            # Check if running on Google Cloud
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                # Use service account from environment
                cred = credentials.ApplicationDefault()
                print("🔑 Using Google Application Default Credentials")
            elif os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY"):
                # Use service account key from environment variable
                import json
                service_account_info = json.loads(os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY"))
                cred = credentials.Certificate(service_account_info)
                print("🔑 Using Firebase Service Account Key from environment")
            else:
                # Try to use service account file
                service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "config/cistech-kg-firebase-adminsdk-fbsvc-bd761a39b2.json")
                if os.path.exists(service_account_path):
                    cred = credentials.Certificate(service_account_path)
                    print(f"🔑 Using Firebase Service Account from {service_account_path}")
                else:
                    print("❌ No Firebase credentials found!")
                    print("Please set one of:")
                    print("  - GOOGLE_APPLICATION_CREDENTIALS environment variable")
                    print("  - FIREBASE_SERVICE_ACCOUNT_KEY environment variable")
                    print("  - FIREBASE_SERVICE_ACCOUNT_PATH environment variable")
                    print("  - Or place service account file at config/firebase-service-account.json")
                    return False
            
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Firebase Admin: {e}")
            return False

async def create_quick_superadmin():
    """Create superadmin with default credentials"""
    
    print("🚀 Quick Superadmin Creation")
    print("=" * 30)
    
    # Initialize Firebase first
    if not initialize_firebase_admin():
        return False
    
    print(f"📧 Email: {DEFAULT_ADMIN['email']}")
    print(f"🔐 Password: {DEFAULT_ADMIN['password']}")
    print(f"👤 Name: {DEFAULT_ADMIN['first_name']} {DEFAULT_ADMIN['last_name']}")
    print(f"📱 Phone: {DEFAULT_ADMIN['phone']}")
    
    try:
        # Step 1: Create Firebase user
        print("\n🔥 Step 1: Creating Firebase user...")
        
        # Check if user already exists
        try:
            firebase_user = auth.get_user_by_email(DEFAULT_ADMIN["email"])
            print(f"🟡 Firebase user {firebase_user.email} already exists. Updating claims...")
            # Update claims for existing user
            auth.set_custom_user_claims(firebase_user.uid, DEFAULT_ADMIN["claims"])
            print("✅ Claims updated successfully")
            
        except auth.UserNotFoundError:
            # Create new user if not found
            firebase_user = auth.create_user(
                email=DEFAULT_ADMIN["email"],
                password=DEFAULT_ADMIN["password"],
                display_name=f"{DEFAULT_ADMIN['first_name']} {DEFAULT_ADMIN['last_name']}",
                email_verified=True
            )
            # Set custom claims for the new user
            auth.set_custom_user_claims(firebase_user.uid, DEFAULT_ADMIN["claims"])
            print(f"✅ Firebase user created: {firebase_user.uid}")
        
        # Step 2: Add user to database
        print("\n🔥 Step 2: Adding user to PostgreSQL database...")
        db = SessionLocal()
        try:
            existing_user = db.query(User).filter(
                User.firebase_uid == firebase_user.uid
            ).first()
            
            if existing_user:
                existing_user.user_type = UserType.SUPERADMIN
                existing_user.first_name = DEFAULT_ADMIN['first_name']
                existing_user.last_name = DEFAULT_ADMIN['last_name']
                existing_user.email = DEFAULT_ADMIN['email']
                existing_user.phone = DEFAULT_ADMIN['phone']
                db.commit()
                user = existing_user
                print(f"✅ Updated existing user: ID {user.id}")
            else:
                user = User(
                    firebase_uid=firebase_user.uid,
                    phone=DEFAULT_ADMIN['phone'],
                    first_name=DEFAULT_ADMIN['first_name'],
                    last_name=DEFAULT_ADMIN['last_name'],
                    email=DEFAULT_ADMIN['email'],
                    user_type=UserType.SUPERADMIN
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"✅ Created new user: ID {user.id}")
        
        except Exception as e:
            db.rollback()
            print(f"❌ Database error: {e}")
            return False
        finally:
            db.close()
        
        print("\n🎉 SUCCESS! Superadmin created!")
        print("\n📋 Login Credentials:")
        print(f"   📧 Email: {DEFAULT_ADMIN['email']}")
        print(f"   🔐 Password: {DEFAULT_ADMIN['password']}")
        print(f"   🆔 User ID: {user.id}")
        print(f"   👑 Role: SUPERADMIN")
        
        print("\n⚠️  SECURITY WARNING:")
        print("   Change the password after first login!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(create_quick_superadmin())
        if success:
            print("\n✅ You can now login to the admin dashboard!")
        else:
            print("\n❌ Failed to create superadmin")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Cancelled")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 