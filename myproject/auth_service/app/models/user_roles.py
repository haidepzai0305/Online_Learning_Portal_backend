from django.db import models

from myproject.auth_service.app.models.roles import Roles
from myproject.auth_service.app.models.users import User


class UserRoles(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'role'], name='user_role_unique')]