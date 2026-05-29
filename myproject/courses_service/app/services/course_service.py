from django.db import transaction
from myproject.courses_service.app.models.courses import Course
from myproject.courses_service.app.models.materials import Material, MaterialType
from myproject.courses_service.app.models.enrollments import Enrollment
from myproject.courses_service.app.models.announcements import Announcement
from myproject.auth_service.app.models.users import User
from myproject.courses_service.app.messaging.publisher import publisher
import logging

logger = logging.getLogger(__name__)

class CourseService:
    @staticmethod
    def create_course(title, description, syllabus, professor_id, **kwargs):
        professor = User.objects.get(pk=professor_id)
        
        course = Course.objects.create(
            title=title,
            description=description,
            syllabus=syllabus,
            professor=professor,
            price=kwargs.get('price', 0.00),
            original_price=kwargs.get('original_price'),
            duration=kwargs.get('duration', '0h'),
            level=kwargs.get('level', 'Beginner'),
            thumbnail_url=kwargs.get('thumbnail_url'),
            learning_outcomes=kwargs.get('learning_outcomes'),
            category=kwargs.get('category', 'frontend')
        )
        
        publisher.publish_event("course_created", {
            "course_id": course.id,
            "title": course.title,
            "professor_id": professor_id
        })
        
        return course

    @staticmethod
    def update_course(course_id, professor_id, **kwargs):
        course = Course.objects.get(pk=course_id)
        if course.professor.id != professor_id:
            raise PermissionError("Only the course owner can modify course content.")
        
        for key, value in kwargs.items():
            if hasattr(course, key):
                setattr(course, key, value)
        course.save()
        return course

    @staticmethod
    def delete_course(course_id, professor_id):
        course = Course.objects.get(pk=course_id)
        if course.professor.id != professor_id:
            raise PermissionError("Only the course owner can delete the course.")
        
        # Check for active enrollments
        if Enrollment.objects.filter(course=course).exists():
            # In a real app, maybe we check if any student has progress > 0 or just confirm
            # For now, let's allow it if the user confirms (caller logic)
            pass
            
        course.delete()

    @staticmethod
    def upload_material(course_id, professor_id, title, material_type, file=None, video_url=None):
        course = Course.objects.get(pk=course_id)
        if course.professor.id != professor_id:
            raise PermissionError("Only the course owner can upload materials.")
            
        material = Material.objects.create(
            course=course,
            title=title,
            material_type=material_type,
            file=file,
            video_url=video_url
        )
        
        publisher.publish_event("material_uploaded", {
            "course_id": course_id,
            "material_id": material.id,
            "title": title,
            "type": material_type
        })
        
        return material

    @staticmethod
    def post_announcement(course_id, professor_id, title, content):
        course = Course.objects.get(pk=course_id)
        if course.professor.id != professor_id:
            raise PermissionError("Only the course owner can post announcements.")
            
        announcement = Announcement.objects.create(
            course=course,
            title=title,
            content=content
        )
        
        publisher.publish_event("announcement_posted", {
            "course_id": course_id,
            "announcement_id": announcement.id,
            "title": title
        })
        
        return announcement

    @staticmethod
    def get_enrolled_students(course_id, professor_id):
        course = Course.objects.get(pk=course_id)
        if course.professor.id != professor_id:
            raise PermissionError("Only the course owner can manage enrolled students.")
            
        return Enrollment.objects.filter(course=course).select_related('student')

    @staticmethod
    def get_course_details(course_id):
        return Course.objects.prefetch_related('materials', 'announcements').get(pk=course_id)

    @staticmethod
    def enroll_student(course_id, student_id):
        course = Course.objects.get(pk=course_id)
        student = User.objects.get(pk=student_id)
        enrollment, created = Enrollment.objects.get_or_create(course=course, student=student)
        
        if created:
            publisher.publish_event("student_enrolled", {
                "course_id": course_id,
                "student_id": student_id,
                "course_title": course.title
            })
            
            # Send confirmation email
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                
                subject = f"Xác nhận thanh toán khóa học: {course.title}"
                message = f"Chào {student.username},\n\nBạn đã thanh toán thành công khóa học '{course.title}'.\nHãy truy cập vào 'Khóa học của tôi' để bắt đầu học nhé!\n\nTrân trọng,\nUniLearn Team"
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@unilearn.com',
                    [student.email],
                    fail_silently=True,
                )
                logger.info(f"Enrollment confirmation email sent successfully to {student.email}")
            except Exception as e:
                logger.error(f"Failed to send enrollment email to {student.email}: {e}")
            
        return enrollment

    @staticmethod
    def update_progress(course_id, student_id, progress):
        enrollment = Enrollment.objects.get(course_id=course_id, student_id=student_id)
        enrollment.progress = progress
        enrollment.save()
        return enrollment

    @staticmethod
    def list_courses(search_query=None, category=None):
        queryset = Course.objects.all()
        if category and category != "all" and category != "":
            queryset = queryset.filter(category__iexact=category)
            
        if search_query:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(category__icontains=search_query)
            )
        return queryset
