import os
import django
import sys

# Add root directory to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.courses_service.app.models.materials import Material

def map_timestamps():
    # Mapping based on typical "Python for Beginners" course (Programming with Mosh)
    # IDs were 3 to 18 for the VIDEO materials of course 2
    mapping = {
        3: 0,      # Python là gì? (Intro/What is Python)
        4: 251,    # Tải và cài đặt (4:11)
        5: 384,    # First Program (6:24)
        6: 504,    # Variables (8:24)
        7: 732,    # Receiving Input (12:12)
        8: 950,    # Type Conversion (15:50)
        9: 1101,   # Strings (18:21)
        10: 1760,  # Arithmetic Operations (29:20)
        11: 2325,  # Comparison Operators (38:45)
        12: 2430,  # If Statements (approx 40:30)
        13: 2700,  # Exercise: Lbs to Kg (approx 45:00)
        14: 2900,  # While Loops (approx 48:20)
        15: 3200,  # Lists (approx 53:20)
        16: 3500,  # List Methods (approx 58:20)
        17: 3800,  # For Loops (approx 1:03:20)
        18: 4100,  # Tuples (approx 1:08:20)
    }
    
    for m_id, start_time in mapping.items():
        try:
            m = Material.objects.get(id=m_id)
            m.start_time = start_time
            m.save()
            print(f"Updated Material {m_id} to start_time {start_time}s")
        except Material.DoesNotExist:
            print(f"Material {m_id} not found")

if __name__ == "__main__":
    map_timestamps()
