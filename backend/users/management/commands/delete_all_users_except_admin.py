from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Delete all users except the super admin (admin@vitmain.com)'

    def handle(self, *args, **options):
        admin_email = 'admin@vitmain.com'
        
        # Get all users except the admin
        users_to_delete = User.objects.exclude(email=admin_email)
        count = users_to_delete.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No users to delete.'))
            return
        
        # Confirm before deletion
        self.stdout.write(f'About to delete {count} user(s).')
        self.stdout.write('Users to be deleted:')
        for user in users_to_delete:
            self.stdout.write(f'  - {user.email} (Role: {user.role})')
        
        # Delete users
        users_to_delete.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} user(s).'))
        self.stdout.write(f'Kept admin user: {admin_email}')
