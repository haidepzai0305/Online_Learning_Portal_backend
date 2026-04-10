"""
Data migration: seed the three RBAC roles (student, professor, admin).
This is idempotent – get_or_create ensures it is safe to run multiple times.
"""
from django.db import migrations


def seed_roles(apps, schema_editor):
    Roles = apps.get_model('app', 'Roles')
    for role_name in ('student', 'professor', 'admin'):
        Roles.objects.get_or_create(name=role_name)


def unseed_roles(apps, schema_editor):
    """Reverse: remove the seeded roles (only if no user is assigned to them)."""
    Roles = apps.get_model('app', 'Roles')
    UserRoles = apps.get_model('app', 'UserRoles')
    for role_name in ('student', 'professor', 'admin'):
        role = Roles.objects.filter(name=role_name).first()
        if role and not UserRoles.objects.filter(role=role).exists():
            role.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_rbac_role_updates'),
    ]

    operations = [
        migrations.RunPython(seed_roles, reverse_code=unseed_roles),
    ]
