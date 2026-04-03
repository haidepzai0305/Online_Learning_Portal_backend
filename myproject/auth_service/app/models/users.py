from django.db import models
from myproject.auth_service.app.enums.users_status import UserStatus

class User(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, default=UserStatus.active)

    class Meta:
        db_table = 'users'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    email_verified = models.BooleanField(default=False)


