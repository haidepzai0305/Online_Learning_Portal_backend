import os
import django
import sys

# Add root directory to sys.path
sys.path.append(os.getcwd())
sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.courses_service.app.models.materials import Material

def check_material_contents():
    materials = Material.objects.filter(course_id=2, material_type='VIDEO')
    for m in materials:
        print(f"--- ID: {m.id} ---")
        print(m.content[:200] if m.content else "No content")
        print("\n")

if __name__ == "__main__":
    check_material_contents()
