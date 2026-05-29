import os
import sys
import django
import bcrypt

# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.auth_service.app.models.users import User
from myproject.auth_service.app.models.user_credentials import UserCredentials
from myproject.auth_service.app.models.user_roles import UserRoles
from myproject.auth_service.app.models.roles import Roles
from myproject.auth_service.app.enums.users_status import UserStatus

def create_student():
    username = 'student_test'
    email = 'student_test@example.com'
    password = 'Student@123'
    
    # 1. Tạo hoặc lấy User
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'status': UserStatus.active}
    )
    
    # 2. Tạo password hash
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # 3. Tạo credentials
    UserCredentials.objects.update_or_create(
        user=user,
        defaults={'password_hash': hashed}
    )
    
    # 4. Gán role student bằng Raw SQL để tránh lỗi thiếu cột ID
    try:
        from django.db import connection
        role = Roles.objects.get(name='student')
        with connection.cursor() as cursor:
            # Kiểm tra xem đã tồn tại chưa
            cursor.execute("SELECT 1 FROM app_userroles WHERE user_id = %s AND role_id = %s", [user.id, role.id])
            if not cursor.fetchone():
                cursor.execute("INSERT INTO app_userroles (user_id, role_id) VALUES (%s, %s)", [user.id, role.id])
        print(f"SUCCESS: Created/Updated user '{username}' with role 'student'")
    except Roles.DoesNotExist:
        print("ERROR: Role 'student' not found in database.")

if __name__ == "__main__":
    create_student()
