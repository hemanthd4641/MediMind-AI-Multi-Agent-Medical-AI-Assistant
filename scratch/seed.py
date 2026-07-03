import sys
import os

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.services.auth_service import AuthService
from backend.app.models.user import UserRole

def seed_admin():
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        
        email = "admin@medimind.ai"
        
        # Check if user already exists
        existing_user = auth_service.user_repo.get_by_email(email)
        if existing_user:
            print(f"User {email} already exists.")
            return

        # Create user
        print(f"Creating user {email}...")
        auth_service.register_user(
            full_name="System Admin",
            email=email,
            password="password123",
            role=UserRole.DOCTOR.value # using doctor role for max permissions based on current setup, or ADMIN if it exists
        )
        print("User created successfully. You can now login with:")
        print(f"Email: {email}")
        print("Password: password123")
    except Exception as e:
        print(f"Error seeding user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin()
