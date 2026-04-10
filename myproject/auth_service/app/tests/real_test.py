import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.auth_service.app.services.auth_service import AuthService
from myproject.auth_service.app.models.users import User

def test_registration():
    email = "test@example.com"
    username = "testuser"
    password = "password123"

    # Clean up if user already exists
    User.objects.filter(email=email).delete()

    try:
        user = AuthService.register_user(email, username, password)
        print(f"Successfully registered: {user.email} (ID: {user.id})")
        
        # Verify it exists in DB
        user_in_db = User.objects.get(email=email)
        print(f"Verified in DB: {user_in_db.username}")
        
    except Exception as e:
        print(f"Expected registration to succeed but failed: {e}")

if __name__ == "__main__":
    test_registration()
