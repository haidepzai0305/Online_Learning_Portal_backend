import datetime

from django.db import models
from django.utils import timezone

from myproject.auth_service.app.models.users import User


class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=255 , db_index=True)
    expires_at = timezone.now() + datetime.timedelta(days=7)
    created_at = models.DateTimeField(auto_now_add=True)
    is_revoked = models.BooleanField(default=False)

    class Meta:
        db_table = 'refresh_tokens'
