import os

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Create the initial deployment administrator from environment variables.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')

        if not username or not email or not password:
            raise CommandError(
                'Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and '
                'DJANGO_SUPERUSER_PASSWORD to create the initial administrator.'
            )

        existing_user = User.objects.filter(username=username).first()
        if existing_user:
            if not existing_user.is_superuser:
                raise CommandError(f'The existing user "{username}" is not a superuser.')
            self.stdout.write(f'Superuser "{username}" already exists.')
            return

        user = User(username=username, email=email, is_staff=True, is_superuser=True)
        try:
            validate_password(password, user)
        except ValidationError as error:
            raise CommandError('; '.join(error.messages)) from error
        user.set_password(password)
        user.save()
        self.stdout.write(self.style.SUCCESS(f'Created superuser "{username}".'))
