from django.db import models

from myproject.auth_service.app.models.users import User


class UserCredentials(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password_hash = models.CharField(max_length = 100 , db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    failed_login_attempts = models.IntegerField(default=0)
    last_login = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_credentials'