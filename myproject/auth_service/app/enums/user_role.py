from django.db import models


class UserRole(models.TextChoices):
    student = "student", "Student"
    professor = "professor", "Professor"
    admin = "admin", "Admin"
