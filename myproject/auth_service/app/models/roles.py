from django.db import models

class Roles(models.Model):
    __tablename__ = 'roles'
    name = models.CharField(max_length=100 , unique=True)

    class Meta:
        db_table = 'roles'