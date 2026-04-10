from django.db import models


class UserStatus(models.TextChoices):
    active =  "active", "Active"
    inactive = "inactive", "Inactive"
    banned = "banned", "Banned"
