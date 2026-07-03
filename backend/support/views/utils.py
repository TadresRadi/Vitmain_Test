import os

from django.contrib.auth import get_user_model

User = get_user_model()

def get_support_admin():
    support_email = os.environ.get("SUPPORT_ACCOUNT_EMAIL", "support@vitmain.com")
    support_admin, created = User.objects.get_or_create(
        email=support_email,
        defaults={
            'full_name': "Vitmain Support",
            'role': 'supervisor',
            'is_staff': True
        }
    )
    if created:
        support_password = os.environ.get("SUPPORT_ACCOUNT_PASSWORD")
        if support_password:
            support_admin.set_password(support_password)
        else:
            support_admin.set_unusable_password()
        support_admin.save(update_fields=["password"])
    return support_admin
