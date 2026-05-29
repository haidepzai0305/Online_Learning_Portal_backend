from django.db import models
from .courses import Course
from myproject.auth_service.app.models.users import User

class CourseQA(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, db_constraint=False)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'course_qa'

class StudentNote(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    student = models.ForeignKey(User, on_delete=models.CASCADE, db_constraint=False)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_notes'
        unique_together = ('course', 'student')
