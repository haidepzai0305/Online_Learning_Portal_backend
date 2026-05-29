import os
import sys
import django
import random

# Thêm thư mục gốc vào sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.auth_service.app.models.users import User
from myproject.auth_service.app.models.roles import Roles
from myproject.courses_service.app.models.courses import Course
from django.db import connection

def seed_data():
    try:
        # 1. Tạo/Lấy Professor
        prof, _ = User.objects.get_or_create(
            username='professor_test', 
            defaults={'email': 'prof@example.com'}
        )
        
        # 2. Gán Role Professor
        role, _ = Roles.objects.get_or_create(name='professor')
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1 FROM app_userroles WHERE user_id = %s AND role_id = %s', [prof.id, role.id])
            if not cursor.fetchone():
                cursor.execute('INSERT INTO app_userroles (user_id, role_id) VALUES (%s, %s)', [prof.id, role.id])
        
        # 3. Danh sách danh mục và mẫu tên khóa học
        categories = {
            "dev": "Development",
            "security": "Security",
            "devops": "DevOps",
            "ai": "AI & Machine Learning",
            "data": "Data Science",
            "mobile": "Mobile Development"
        }
        
        levels = ["Beginner", "Intermediate", "Advanced"]
        
        print("Starting seeding process...")
        
        for cat_id, cat_name in categories.items():
            print(f"Generating courses for category: {cat_name}...")
            for i in range(1, 5):
                title = f"{cat_name} Course #{i}: Master the Essentials"
                if i == 2: title = f"Advanced {cat_name} for Professionals"
                if i == 3: title = f"{cat_name} Zero to Hero 2026"
                if i == 4: title = f"The Complete {cat_name} Bootcamp"
                
                course, created = Course.objects.get_or_create(
                    title=title,
                    defaults={
                        'description': f"This is a comprehensive course about {cat_name}. Learn all the skills you need to become a pro in this field.",
                        'professor': prof,
                        'price': random.choice([19.99, 29.99, 49.99, 99.99]),
                        'original_price': random.choice([120.00, 150.00, 200.00]),
                        'category': cat_id,
                        'level': random.choice(levels),
                        'duration': f"{random.randint(5, 40)}h",
                        'rating': round(random.uniform(4.0, 5.0), 1),
                        'review_count': random.randint(100, 5000)
                    }
                )
                if created:
                    print(f"  - Created: {title}")
                else:
                    print(f"  - Already exists: {title}")

        print("\nSUCCESS: All categories now have 4 courses each.")

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    seed_data()
