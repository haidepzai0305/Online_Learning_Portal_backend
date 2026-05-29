from django.core.management.base import BaseCommand
from myproject.courses_service.app.models.courses import Course

class Command(BaseCommand):
    help = 'Sets all course prices to 2000 VND'

    def handle(self, *args, **options):
        count = Course.objects.all().update(price=2000, original_price=5000)
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {count} courses to 2000 VND'))
