import os
import django
import sys

# Add root directory to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from myproject.courses_service.app.models.materials import Material
from myproject.ai_service.app.services.rag_service import RAGService

def index_all_materials():
    print("Starting indexing process...")
    materials = Material.objects.exclude(content__isnull=True).exclude(content='')
    
    # Clear vector store first
    RAGService._load_storage()
    courses_to_index = set(str(m.course.id) for m in materials)
    for course_id in courses_to_index:
        RAGService._vector_store[course_id] = []
    
    count = 0
    for material in materials:
        print(f"Indexing Material ID {material.id}")
        metadata = {
            "material_id": material.id,
            "start_time": material.start_time,
            "title": material.title
        }
        RAGService.index_document(str(material.course.id), material.content, metadata=metadata)
        count += 1
    
    print(f"SUCCESS: Indexed {count} materials.")

if __name__ == "__main__":
    index_all_materials()
