from django.core.management.base import BaseCommand
from django.utils import timezone

from castellum.castellum_auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser with fixed credentials'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            expiration_date = timezone.now() + timezone.timedelta(days=1000)
            User.objects.create_superuser(
                'admin', 'admin@example.com', '123', expiration_date=expiration_date)
