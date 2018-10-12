import os
import django


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'backend.settings'
)
django.setup()

from kidsbook.models import *  # noqa

print("COME HRERE")
User.objects.create_superuser(
    email_address='a@a.com',
    username='a',
    password='a'
)
