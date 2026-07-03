import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from subscriptions.models import Plan

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial plans, super admin user, and basic configuration data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding initial data...')

        # 1. Seed Plans
        plans_data = [
            {
                'name': 'Professional',
                'slug': 'basic',
                'price': 200.00,
                'description': 'AI campaign posts and image generation.',
                'features': '10 AI posts,Image generation,Post editing,Website promotion'
            },
            {
                'name': 'Full Marketing Plan',
                'slug': 'pro',
                'price': 5000.00,
                'description': 'Dedicated expert campaign team via support.',
                'features': 'Personal account manager,Priority support,Custom strategies'
            }
        ]

        for p_data in plans_data:
            plan, created = Plan.objects.update_or_create(
                slug=p_data['slug'],
                defaults={
                    'name': p_data['name'],
                    'price': p_data['price'],
                    'description': p_data['description'],
                    'features': p_data['features']
                }
            )
            if created:
                self.stdout.write(f"Plan '{plan.name}' created.")
            else:
                self.stdout.write(f"Plan '{plan.name}' updated.")

        # 2. Seed Super Admin User
        admin_email = os.environ.get('SEED_ADMIN_EMAIL', 'admin@vitmain.com')
        admin_password = os.environ.get('SEED_ADMIN_PASSWORD')
        
        if not User.objects.filter(email=admin_email).exists():
            if not admin_password:
                raise RuntimeError("SEED_ADMIN_PASSWORD env var is required to create the initial super admin.")

            admin_user = User.objects.create_superuser(
                email=admin_email,
                password=admin_password,
                full_name='Vitmain Super Admin',
                phone_number='+15550199',
                user_type='business_owner',
                role='super_admin'
            )
            self.stdout.write(f"Super Admin user created successfully: {admin_email}")
        else:
            self.stdout.write(f"Super Admin user '{admin_email}' already exists.")

        self.stdout.write(self.style.SUCCESS('Successfully seeded all initial database resources.'))
