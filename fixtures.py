import os
import django


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'backend.settings'
)
django.setup()

from kidsbook.models import *  # noqa

print("COME HRERE")
User.objects.create_roles()
User.objects.create_superuser(
    email_address='a@a.com',
    username='a',
    password='a',
    role=1
)

HIEU = User.objects.create_superuser(
    email_address='hieu@gmail.com',
    username='hieu',
    password='a',
    role=1
)

SON = User.objects.create_superuser(
    email_address='son@gmail.com',
    username='son',
    password='a',
    role=0
)

HIEU_POST = Post.objects.create_post(
    content='Need someone to eat lunch at pgp?',
    creator= HIEU
)

SON_COMMENT = Comment.objects.create_comment(
    content = 'OKAY',
    post_id = HIEU_POST,
    creator= SON
)

HIEU_GROUP = Group.objects.create_group(
    name='HIEU_GROUP',
    creator = HIEU
)

HIEU_GROUP.add_member(SON)
