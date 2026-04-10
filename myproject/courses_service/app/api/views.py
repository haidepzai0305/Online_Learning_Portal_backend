import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myproject.auth_service.app.utils.auth_middleware import jwt_required, role_required
from myproject.courses_service.app.services.course_service import CourseService
from myproject.courses_service.app.models.materials import MaterialType

logger = logging.getLogger(__name__)

# ─── Courses CRUD ───────────────────────────────────────────────

@csrf_exempt
@jwt_required
@role_required("professor", "admin")
def create_course_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        title = data.get("title")
        description = data.get("description")
        syllabus = data.get("syllabus")
        
        if not title or not description:
            return JsonResponse({"error": "Title and description are required"}, status=400)
            
        course = CourseService.create_course(title, description, syllabus, request.user_id)
        return JsonResponse({
            "message": "Course created successfully",
            "course": {
                "id": course.id,
                "title": course.title,
                "description": course.description
            }
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
def list_courses_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    courses = CourseService.list_courses()
    data = [{
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "professor": c.professor.username
    } for c in courses]
    
    return JsonResponse({"courses": data})

@csrf_exempt
@jwt_required
def get_course_detail_view(request, course_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        course = CourseService.get_course_details(course_id)
        materials = [{
            "id": m.id,
            "title": m.title,
            "type": m.material_type,
            "file_url": m.file.url if m.file else None,
            "video_url": m.video_url
        } for m in course.materials.all()]
        
        announcements = [{
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "created_at": a.created_at.isoformat()
        } for a in course.announcements.all()]
        
        return JsonResponse({
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "syllabus": course.syllabus,
            "professor": course.professor.username,
            "materials": materials,
            "announcements": announcements
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=404)

@csrf_exempt
@jwt_required
@role_required("professor", "admin")
def update_course_view(request, course_id):
    if request.method not in ["PUT", "PATCH"]:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        course = CourseService.update_course(course_id, request.user_id, **data)
        return JsonResponse({"message": "Course updated successfully"})
    except PermissionError as e:
        return JsonResponse({"error": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
@role_required("professor", "admin")
def delete_course_view(request, course_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        CourseService.delete_course(course_id, request.user_id)
        return JsonResponse({"message": "Course deleted successfully"})
    except PermissionError as e:
        return JsonResponse({"error": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# ─── Materials ──────────────────────────────────────────────────

@csrf_exempt
@jwt_required
@role_required("professor", "admin")
def upload_material_view(request, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        title = request.POST.get("title")
        material_type = request.POST.get("material_type")
        video_url = request.POST.get("video_url")
        file = request.FILES.get("file")
        
        if not title or not material_type:
            return JsonResponse({"error": "Title and material_type are required"}, status=400)
            
        material = CourseService.upload_material(
            course_id, request.user_id, title, material_type, file, video_url
        )
        return JsonResponse({
            "message": "Material uploaded successfully",
            "material_id": material.id
        }, status=201)
    except PermissionError as e:
        return JsonResponse({"error": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# ─── Announcements ──────────────────────────────────────────────

@csrf_exempt
@jwt_required
@role_required("professor", "admin")
def post_announcement_view(request, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        title = data.get("title")
        content = data.get("content")
        
        if not title or not content:
            return JsonResponse({"error": "Title and content are required"}, status=400)
            
        announcement = CourseService.post_announcement(course_id, request.user_id, title, content)
        return JsonResponse({
            "message": "Announcement posted successfully",
            "announcement_id": announcement.id
        }, status=201)
    except PermissionError as e:
        return JsonResponse({"error": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# ─── Students & Enrollment ─────────────────────────────────────

@csrf_exempt
@jwt_required
@role_required("professor", "admin")
def list_enrolled_students_view(request, course_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        enrollments = CourseService.get_enrolled_students(course_id, request.user_id)
        data = [{
            "student_id": e.student.id,
            "username": e.student.username,
            "email": e.student.email,
            "progress": e.progress,
            "enrolled_at": e.enrolled_at.isoformat()
        } for e in enrollments]
        return JsonResponse({"students": data})
    except PermissionError as e:
        return JsonResponse({"error": str(e)}, status=403)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
@role_required("student")
def enroll_course_view(request, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        enrollment = CourseService.enroll_student(course_id, request.user_id)
        return JsonResponse({"message": "Enrolled successfully"}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
def update_progress_view(request, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        progress = data.get("progress")
        if progress is None:
            return JsonResponse({"error": "Progress value is required"}, status=400)
            
        enrollment = CourseService.update_progress(course_id, request.user_id, int(progress))
        return JsonResponse({
            "message": "Progress updated successfully",
            "progress": enrollment.progress
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
