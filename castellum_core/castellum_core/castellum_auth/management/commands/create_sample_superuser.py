from django.core.management.base import BaseCommand
from django.utils import timezone

from castellum_auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser with fixed credentials'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', '123')
