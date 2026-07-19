"""
Management command to create a performance test user.
Usage: python manage.py create_perf_user
"""
from django.core.management.base import BaseCommand
from users.models import CustomUser


class Command(BaseCommand):
    help = 'Create a performance test user for locust load testing'

    def handle(self, *args, **options):
        email = 'perf-test@example.com'
        password = 'TestPass123!'

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'is_email_verified': True,
                'role': 'user',
            }
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created perf-test user: {email}')
            )
        else:
            user.set_password(password)
            user.is_email_verified = True
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated perf-test user: {email}')
            )

        self.stdout.write(f'  Email:    {email}')
        self.stdout.write(f'  Password: {password}')