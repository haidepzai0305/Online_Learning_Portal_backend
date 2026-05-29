from django.db import transaction
from django.utils import timezone
from myproject.courses_service.app.models.assignments import Assignment
from myproject.courses_service.app.models.submissions import Submission
from myproject.courses_service.app.models.courses import Course
from myproject.auth_service.app.models.users import User
from myproject.courses_service.app.messaging.publisher import publisher

class AssignmentService:
    @staticmethod
    def create_assignment(course_id, professor_id, title, description, deadline, max_score=100.00):
        course = Course.objects.get(pk=course_id)
        if course.professor.id != professor_id:
            raise PermissionError("Only the course owner can create assignments.")
        
        assignment = Assignment.objects.create(
            course=course,
            title=title,
            description=description,
            deadline=deadline,
            max_score=max_score
        )
        
        publisher.publish_event("assignment_posted", {
            "course_id": course_id,
            "assignment_id": assignment.id,
            "title": title,
            "deadline": str(deadline)
        })
        
        return assignment

    @staticmethod
    def get_assignments(course_id):
        return Assignment.objects.filter(course_id=course_id)

    @staticmethod
    def submit_assignment(assignment_id, student_id, file_url):
        assignment = Assignment.objects.get(pk=assignment_id)
        student = User.objects.get(pk=student_id)
        
        is_late = timezone.now() > assignment.deadline
        
        submission, created = Submission.objects.update_or_create(
            assignment=assignment,
            student=student,
            defaults={
                'file_url': file_url,
                'is_late': is_late,
                'submitted_at': timezone.now()
            }
        )
        
        publisher.publish_event("assignment_submitted", {
            "assignment_id": assignment_id,
            "student_id": student_id,
            "is_late": is_late
        })
        
        return submission

    @staticmethod
    def grade_submission(submission_id, professor_id, score, feedback=None):
        submission = Submission.objects.get(pk=submission_id)
        if submission.assignment.course.professor.id != professor_id:
            raise PermissionError("Only the course owner can grade submissions.")
        
        if score > submission.assignment.max_score:
            raise ValueError(f"Score cannot exceed max score of {submission.assignment.max_score}")
            
        submission.score = score
        submission.feedback = feedback
        submission.save()
        
        publisher.publish_event("submission_graded", {
            "submission_id": submission_id,
            "student_id": submission.student.id,
            "score": float(score)
        })
        
        return submission

    @staticmethod
    def get_performance_summary(student_id):
        submissions = Submission.objects.filter(student_id=student_id, score__isnull=False)
        if not submissions.exists():
            return {"average_score": 0, "total_submissions": 0}
        
        total_score = sum(s.score for s in submissions)
        count = submissions.count()
        avg = float(total_score / count)
        
        return {
            "average_score": avg,
            "total_submissions": count,
            "submissions": [{
                "assignment": s.assignment.title,
                "score": float(s.score)
            } for s in submissions]
        }

    @staticmethod
    def get_weak_topics(course_id, professor_id):
        course = Course.objects.get(pk=course_id)
        if course.professor.id != professor_id:
            raise PermissionError("Only the professor can view class statistics.")
            
        assignments = Assignment.objects.filter(course_id=course_id)
        weak_topics = []
        
        for a in assignments:
            scores = Submission.objects.filter(assignment=a, score__isnull=False).values_list('score', flat=True)
            if scores:
                avg = sum(scores) / len(scores)
                if avg < (float(a.max_score) * 0.6):
                    weak_topics.append({
                        "topic": a.title,
                        "average_score": float(avg)
                    })
        
        return weak_topics
