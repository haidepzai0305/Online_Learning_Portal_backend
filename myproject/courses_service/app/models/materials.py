from django.db import models
from .courses import Course

class MaterialType(models.TextChoices):
    PDF = 'PDF', 'PDF Document'
    DOCX = 'DOCX', 'Word Document'
    PPT = 'PPT', 'PowerPoint Presentation'
    VIDEO = 'VIDEO', 'Video Link'
    OTHER = 'OTHER', 'Other'

class Material(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=255)
    material_type = models.CharField(max_length=10, choices=MaterialType.choices)
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'materials'

    def __str__(self):
        return f"{self.title} ({self.material_type})"
