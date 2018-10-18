import os
import django


os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', 'backend.settings'
)
django.setup()

from kidsbook.models import *  # noqa

print("COME HERE")
User.objects.create_roles()
User.objects.create_superuser(
    email_address='a@a.com',
    username='a',
    password='a'
)

HIEU = User.objects.create_superuser(
    email_address='hieu@gmail.com',
    username='hieu',
    password='a'
)

SON = User.objects.create_superuser(
    email_address='son@gmail.com',
    username='son',
    password='a'
)

HIEU_GROUP = Group.objects.create_group(
    name='HIEU_GROUP',
    creator = HIEU
)

HIEU_GROUP.add_member(SON)

SON_GROUP = Group.objects.create_group(
    name='SON_GROUP',
    creator = SON
)


HIEU_POST = Post.objects.create_post(
    content='Need someone to eat lunch at pgp?',
    creator= HIEU,
    group=HIEU_GROUP
)

SON_COMMENT = Comment.objects.create_comment(
    content = 'OKAY',
    post = HIEU_POST,
    creator= SON
)
