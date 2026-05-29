from django.db import models
from .assignments import Assignment
from myproject.auth_service.app.models.users import User

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions', db_constraint=False)
    file_url = models.CharField(max_length=500)  # Link to the uploaded file
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    is_late = models.BooleanField(default=False)

    class Meta:
        db_table = 'submissions'
        unique_together = ('assignment', 'student') # One submission per student per assignment

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
