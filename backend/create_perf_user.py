from users.models import CustomUser

user, created = CustomUser.objects.get_or_create(
    email='perf-test@example.com',
    defaults={
        'is_email_verified': True,
        'role': 'user',
    }
)
if created:
    user.set_password('TestPass123!')
    user.save()
    print('Created perf-test user')
else:
    print('perf-test user already exists')