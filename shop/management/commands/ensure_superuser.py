import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Muhit o'zgaruvchilaridan admin foydalanuvchi yaratadi (mavjud bo'lsa tegilmaydi)."

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()

        if not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_PASSWORD berilmagan — admin yaratilmadi."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(f"'{username}' admin allaqachon mavjud.")
            return

        User.objects.create_superuser(username, email, password)
        self.stdout.write(self.style.SUCCESS(f"'{username}' admin yaratildi."))
