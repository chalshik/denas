#!/usr/bin/env python3
"""
Script to create a superadmin user in the CisTech marketplace.

This script will:
1. Create a Firebase user with email/password
2. Set Firebase custom claims for SUPERADMIN role
3. Add the user to the PostgreSQL database
4. Verify the user was created successfully

Usage:
    python scripts/create_superadmin.py

Make sure to set up your environment variables properly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to Python path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User, UserType
from app.services.firebase_service import FirebaseService
from firebase_admin import auth
import firebase_admin
from firebase_admin import credentials
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e

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

async def create_superadmin_user():
    """Create a superadmin user"""
    
    print("🚀 CisTech Superadmin User Creation")
    print("=" * 50)
    
    # Initialize Firebase first
    if not initialize_firebase_admin():
        return False
    
    # Get user input
    email = input("📧 Enter admin email address: ").strip()
    if not email:
        print("❌ Email is required!")
        return False
    
    password = input("🔐 Enter admin password: ").strip()
    if not password:
        print("❌ Password is required!")
        return False
    
    if len(password) < 6:
        print("❌ Password must be at least 6 characters!")
        return False
    
    first_name = input("👤 Enter first name: ").strip() or "Super"
    last_name = input("👤 Enter last name: ").strip() or "Admin"
    phone = input("📱 Enter phone number (e.g., +1234567890): ").strip()
    
    if not phone:
        # Generate a unique phone number for admin
        import time
        phone = f"+999{int(time.time())}"  # Unique phone for admin
        print(f"📱 Generated admin phone: {phone}")
    
    print(f"\n📋 Creating superadmin user:")
    print(f"   Email: {email}")
    print(f"   Name: {first_name} {last_name}")
    print(f"   Phone: {phone}")
    
    confirm = input("\n✅ Proceed? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled by user")
        return False
    
    try:
        print("\n🔥 Step 1: Creating Firebase user...")
        
        # Create Firebase user
        try:
            firebase_user = auth.create_user(
                email=email,
                password=password,
                phone_number=phone,
                email_verified=True,
                display_name=f"{first_name} {last_name}"
            )
            print(f"✅ Firebase user created: {firebase_user.uid}")
        except auth.EmailAlreadyExistsError:
            print(f"⚠️  Email already exists in Firebase, getting existing user...")
            firebase_user = auth.get_user_by_email(email)
            print(f"✅ Found existing Firebase user: {firebase_user.uid}")
        except Exception as e:
            print(f"❌ Error creating Firebase user: {e}")
            return False
        
        print("\n🔧 Step 2: Setting Firebase custom claims...")
        
        # Set custom claims for SUPERADMIN
        success, message = await FirebaseService.set_admin_role(
            firebase_user.uid, 
            "SUPERADMIN"
        )
        
        if success:
            print(f"✅ Firebase claims set: {message}")
        else:
            print(f"❌ Failed to set Firebase claims: {message}")
            return False
        
        print("\n💾 Step 3: Adding user to database...")
        
        # Add user to database
        db = get_db()
        try:
            # Check if user already exists in database
            existing_user = db.query(User).filter(
                User.firebase_uid == firebase_user.uid
            ).first()
            
            if existing_user:
                # Update existing user
                existing_user.user_type = UserType.SUPERADMIN
                existing_user.first_name = first_name
                existing_user.last_name = last_name
                existing_user.email = email
                existing_user.phone = phone
                db.commit()
                db.refresh(existing_user)
                user = existing_user
                print(f"✅ Updated existing database user: ID {user.id}")
            else:
                # Create new user
                user = User(
                    firebase_uid=firebase_user.uid,
                    phone=phone,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    user_type=UserType.SUPERADMIN
                )
                
                db.add(user)
                db.commit()
                db.refresh(user)
                print(f"✅ Database user created: ID {user.id}")
        
        except Exception as e:
            db.rollback()
            print(f"❌ Database error: {e}")
            return False
        finally:
            db.close()
        
        print("\n🔍 Step 4: Verifying user creation...")
        
        # Verify Firebase claims
        firebase_user_updated = auth.get_user(firebase_user.uid)
        claims = firebase_user_updated.custom_claims or {}
        user_type = claims.get("user_type")
        
        if user_type == "SUPERADMIN":
            print("✅ Firebase claims verified: SUPERADMIN")
        else:
            print(f"❌ Firebase claims verification failed: {user_type}")
            return False
        
        # Verify database
        db = get_db()
        try:
            db_user = db.query(User).filter(
                User.firebase_uid == firebase_user.uid
            ).first()
            
            if db_user and db_user.user_type == UserType.SUPERADMIN:
                print("✅ Database user verified: SUPERADMIN")
            else:
                print(f"❌ Database verification failed: {db_user.user_type if db_user else 'User not found'}")
                return False
        finally:
            db.close()
        
        print("\n🎉 SUCCESS! Superadmin user created successfully!")
        print(f"📧 Email: {email}")
        print(f"🔐 Password: {password}")
        print(f"🆔 Firebase UID: {firebase_user.uid}")
        print(f"🏢 Database ID: {user.id}")
        print(f"👑 Role: SUPERADMIN")
        
        print("\n🚨 IMPORTANT:")
        print("1. Save the password securely!")
        print("2. You can now login to the admin dashboard")
        print("3. Consider changing the password after first login")
        
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.error(f"Error creating superadmin: {e}", exc_info=True)
        return False

async def list_existing_admins():
    """List existing admin users"""
    print("\n📋 Existing Admin Users:")
    print("=" * 30)
    
    db = get_db()
    try:
        admin_users = db.query(User).filter(
            User.user_type.in_([UserType.ADMIN, UserType.SUPERADMIN])
        ).all()
        
        if not admin_users:
            print("No admin users found.")
            return
        
        for user in admin_users:
            print(f"👤 {user.first_name} {user.last_name}")
            print(f"   📧 Email: {user.email}")
            print(f"   📱 Phone: {user.phone}")
            print(f"   👑 Role: {user.user_type.value}")
            print(f"   🆔 ID: {user.id}")
            print(f"   🔥 Firebase UID: {user.firebase_uid}")
            print()
    
    except Exception as e:
        print(f"❌ Error listing admins: {e}")
    finally:
        db.close()

async def main():
    """Main function"""
    print("🔧 CisTech Admin User Management")
    print("=" * 40)
    print("1. Create new superadmin user")
    print("2. List existing admin users")
    print("3. Exit")
    
    while True:
        choice = input("\nChoose an option (1-3): ").strip()
        
        if choice == "1":
            success = await create_superadmin_user()
            if success:
                break
        elif choice == "2":
            await list_existing_admins()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    try:
        # Run the async main function
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 