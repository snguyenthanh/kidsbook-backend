import os
import django


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'backend.settings'
)
django.setup()

from main.models import *  # noqa

User.objects.create_superuser(
    email_address='a@a.com',
    username='a',
    password='a'
)
