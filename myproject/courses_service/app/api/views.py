import os
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from myproject.auth_service.app.utils.auth_middleware import jwt_required, role_required
from myproject.courses_service.app.services.course_service import CourseService
from myproject.courses_service.app.services.assignment_service import AssignmentService
from myproject.courses_service.app.models.materials import MaterialType, Material
from myproject.courses_service.app.models.enrollments import Enrollment
from myproject.courses_service.app.utils.streaming import get_range_response
from django.http import FileResponse, StreamingHttpResponse

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
            
        course = CourseService.create_course(
            title=title, 
            description=description, 
            syllabus=syllabus, 
            professor_id=request.user_id,
            **data
        )
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
def list_courses_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    search_query = request.GET.get('search') or request.GET.get('q')
    category = request.GET.get('category')
    courses = CourseService.list_courses(search_query=search_query, category=category)
    data = [{
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "instructor": c.professor.username,
        "price": float(c.price),
        "originalPrice": float(c.original_price) if c.original_price else float(c.price),
        "duration": c.duration,
        "level": c.level,
        "rating": c.rating,
        "reviewCount": c.review_count,
        "thumbnail": c.thumbnail_url if c.thumbnail_url else "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=800&q=80",
        "category": c.category,
        "students": 1200 # Dummy for now
    } for c in courses]

    # Mapping for category IDs to display names (Case-insensitive)
    CAT_MAP = {
        "dev": "Development",
        "frontend": "Development",
        "backend": "Development",
        "security": "Security",
        "devops": "DevOps",
        "ai": "AI & Machine Learning",
        "machine learning": "AI & Machine Learning",
        "artificial intelligence": "AI & Machine Learning",
        "data": "Data Science",
        "mobile": "Mobile Development"
    }

    # Calculate global totals per category (ignoring search and category filters)
    global_results = CourseService.list_courses(search_query=None)
    category_counts = {}
    for c in global_results:
        db_cat = (c.category or "").lower().strip()
        # Fallback to capitalize if not in map
        display_name = CAT_MAP.get(db_cat, db_cat.capitalize() if db_cat else "Other")
        category_counts[display_name] = category_counts.get(display_name, 0) + 1

    # Categories to return to frontend
    sidebar_categories = [
        {"id": "dev", "name": "Development"},
        {"id": "security", "name": "Security"},
        {"id": "devops", "name": "DevOps"},
        {"id": "ai", "name": "AI & Machine Learning"},
        {"id": "data", "name": "Data Science"},
        {"id": "mobile", "name": "Mobile Development"},
    ]
    
    final_categories = []
    for sc in sidebar_categories:
        final_categories.append({
            "id": sc["id"],
            "name": sc["name"],
            "count": category_counts.get(sc["name"], 0)
        })
    
    return JsonResponse({
        "courses": data, 
        "categories": final_categories,
        "total": len(courses) # This is for the "X courses found" banner
    })

@csrf_exempt
@jwt_required
@role_required("professor", "admin")
def list_my_courses_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    from myproject.courses_service.app.models.courses import Course
    courses = Course.objects.filter(professor_id=request.user_id)
    data = [{
        "id": c.id,
        "title": c.title,
        "price": float(c.price),
        "students": 0, # TODO
        "status": "Published",
        "category": c.category
    } for c in courses]
    
    return JsonResponse({"courses": data})

@csrf_exempt
def get_course_detail_view(request, course_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        course = CourseService.get_course_details(course_id)
        
        # Calculate students count
        from myproject.courses_service.app.models.enrollments import Enrollment
        student_count = Enrollment.objects.filter(course=course).count()

        # Check if requesting user is enrolled
        is_enrolled = False
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from jose import jwt
                from myproject.auth_service.app.core.config import settings
                token = auth_header.split(' ')[1]
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_id = payload.get('user_id')
                if user_id:
                    is_enrolled = Enrollment.objects.filter(course=course, student_id=user_id).exists()
            except Exception:
                pass

        materials = [{
            "id": m.id,
            "title": m.title,
            "type": m.material_type,
            "file_url": m.file.url if m.file else None,
            "video_url": m.video_url,
            "stream_url": f"/api/courses/materials/{m.id}/stream/" if m.material_type == MaterialType.VIDEO and m.file else None,
            "start_time": m.start_time,
            "content": m.content
        } for m in course.materials.all().order_by('order')]
        
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
            "instructor": course.professor.username,
            "price": float(course.price),
            "originalPrice": float(course.original_price) if course.original_price else float(course.price),
            "duration": course.duration,
            "level": course.level,
            "thumbnail": course.thumbnail_url or "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=400&h=300&fit=crop",
            "rating": course.rating,
            "reviewCount": course.review_count,
            "students": student_count,
            "is_enrolled": is_enrolled,
            "category": course.category,
            "learningGoals": course.learning_outcomes.split('\n') if course.learning_outcomes else [],
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
@role_required("student", "professor", "admin")
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
@role_required("student", "professor", "admin")
def list_student_enrollments_view(request):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    from myproject.courses_service.app.models.enrollments import Enrollment
    enrollments = Enrollment.objects.filter(student_id=request.user_id).select_related('course')
    
    data = [{
        "id": e.course.id,
        "title": e.course.title,
        "category": e.course.category,
        "thumbnail": e.course.thumbnail_url or "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=600&q=80",
        "progress": e.progress,
        "purchaseDate": e.enrolled_at.strftime("%d/%m/%Y")
    } for e in enrollments]
    
    return JsonResponse({"courses": data})

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

# ─── Assignments & Submissions ──────────────────────────────────

@csrf_exempt
@jwt_required
@role_required("professor", "admin")
def create_assignment_view(request, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        assignment = AssignmentService.create_assignment(
            course_id=course_id,
            professor_id=request.user_id,
            title=data.get("title"),
            description=data.get("description"),
            deadline=data.get("deadline"),
            max_score=data.get("max_score", 100.00)
        )
        return JsonResponse({
            "message": "Assignment created successfully",
            "assignment_id": assignment.id
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
def list_assignments_view(request, course_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        assignments = AssignmentService.get_assignments(course_id)
        data = [{
            "id": a.id,
            "title": a.title,
            "description": a.description,
            "deadline": a.deadline.isoformat(),
            "max_score": float(a.max_score)
        } for a in assignments]
        return JsonResponse({"assignments": data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
@role_required("student")
def submit_assignment_view(request, assignment_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        file_url = data.get("file_url")
        if not file_url:
            return JsonResponse({"error": "file_url is required"}, status=400)
            
        submission = AssignmentService.submit_assignment(
            assignment_id=assignment_id,
            student_id=request.user_id,
            file_url=file_url
        )
        return JsonResponse({
            "message": "Assignment submitted successfully",
            "submission_id": submission.id,
            "is_late": submission.is_late
        }, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
@role_required("professor", "admin")
def grade_submission_view(request, submission_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        score = data.get("score")
        feedback = data.get("feedback")
        
        if score is None:
            return JsonResponse({"error": "score is required"}, status=400)
            
        submission = AssignmentService.grade_submission(
            submission_id=submission_id,
            professor_id=request.user_id,
            score=float(score),
            feedback=feedback
        )
        return JsonResponse({
            "message": "Submission graded successfully",
            "score": float(submission.score)
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# ─── Video Streaming ──────────────────────────────────────────

@csrf_exempt
@jwt_required
def stream_video_view(request, material_id):
    """
    Streams a video material file using Range requests.
    """
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
        
    try:
        material = Material.objects.get(pk=material_id)
        
        # Security check: User must be professor or enrolled student
        course = material.course
        is_owner = (course.professor_id == request.user_id)
        is_enrolled = Enrollment.objects.filter(course=course, student_id=request.user_id).exists()
        
        if not (is_owner or is_enrolled):
            return JsonResponse({"error": "You do not have permission to access this video."}, status=403)
            
        if material.material_type != MaterialType.VIDEO or not material.file:
            return JsonResponse({"error": "This material is not a streamable video file."}, status=400)
            
        file_path = material.file.path
        if not os.path.exists(file_path):
            return JsonResponse({"error": "Video file not found on server."}, status=404)
            
        range_header = request.headers.get('Range', None)
        
        if not range_header:
            # Return full file or a simple FileResponse if no range requested
            # Browser usually sends Range: bytes=0- first
            return FileResponse(open(file_path, 'rb'), content_type='video/mp4')
            
        response = get_range_response(file_path, range_header)
        if not response:
            return JsonResponse({"error": "Invalid range requested"}, status=416)
            
        return response
        
    except Material.DoesNotExist:
        return JsonResponse({"error": "Material not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ─── Interactions (QA & Notes) ─────────────────────────────────

from myproject.courses_service.app.models.interactions import CourseQA, StudentNote

@csrf_exempt
@jwt_required
def get_course_qa_view(request, course_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    qa_list = CourseQA.objects.filter(course_id=course_id).order_by('-created_at')
    data = [{
        "id": q.id,
        "user": q.student.username,
        "date": q.created_at.strftime("%d/%m/%Y"),
        "question": q.question,
        "answer": q.answer
    } for q in qa_list]
    return JsonResponse({"qa": data})

@csrf_exempt
@jwt_required
def post_course_qa_view(request, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        question = data.get("question")
        if not question:
            return JsonResponse({"error": "Question is required"}, status=400)
            
        qa = CourseQA.objects.create(
            course_id=course_id,
            student_id=request.user_id,
            question=question
        )
        return JsonResponse({"message": "Question posted", "id": qa.id}, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
@jwt_required
def get_student_note_view(request, course_id):
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        note = StudentNote.objects.get(course_id=course_id, student_id=request.user_id)
        return JsonResponse({"content": note.content})
    except StudentNote.DoesNotExist:
        return JsonResponse({"content": ""})

@csrf_exempt
@jwt_required
def save_student_note_view(request, course_id):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        content = data.get("content")
        
        note, created = StudentNote.objects.update_or_create(
            course_id=course_id,
            student_id=request.user_id,
            defaults={'content': content}
        )
        return JsonResponse({"message": "Note saved successfully"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
