from django.db import models
from myproject.auth_service.app.models.users import User

class UserSocialAuth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_auths')
    provider = models.CharField(max_length=50) # 'google' or 'microsoft'
    provider_id = models.CharField(max_length=255)
    extra_data = models.TextField(null=True, blank=True) # store extra fields (e.g. profile pic url, etc.)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_social_auth'
        unique_together = ('provider', 'provider_id')

    def __str__(self):
        return f"{self.user.email} - {self.provider}"
