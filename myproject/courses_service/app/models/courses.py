from django.db import models
from myproject.auth_service.app.models.users import User

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    syllabus = models.TextField(blank=True, null=True)
    professor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_courses', db_constraint=False)
    
    # New metadata fields for frontend
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    duration = models.CharField(max_length=50, default="0h")
    level = models.CharField(max_length=50, default="Beginner")
    thumbnail_url = models.URLField(max_length=500, null=True, blank=True)
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    learning_outcomes = models.TextField(help_text="Newline separated goals", blank=True, null=True)
    category = models.CharField(max_length=100, default="frontend")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return self.title
