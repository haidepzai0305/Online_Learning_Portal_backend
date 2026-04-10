from django.db import models

from myproject.auth_service.app.models.users import User


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'email_verification_tokens'