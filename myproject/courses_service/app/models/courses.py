from django.db import models
from myproject.auth_service.app.models.users import User

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    syllabus = models.TextField(blank=True, null=True)
    professor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return self.title
