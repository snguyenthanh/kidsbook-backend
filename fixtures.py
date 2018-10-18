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
    username='Best teacher',
    password='a',
    role=1,
    description='Call me by A',
    realname="Sreyans Sipanis"
)

HIEU = User.objects.create_superuser(
    email_address='hieu@gmail.com',
    username='Tall Guy',
    password='a',
    role=1,
    description='Call me by Hieu',
    realname="Le Trung Hieu"
)

SON = User.objects.create_superuser(
    email_address='son@gmail.com',
    username='Assasin',
    password='a',
    role=0,
    description='Call me by Son',
    realname="Nguyen Thanh Son"
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

HIEU_POST2 = Post.objects.create_post(
    content='Need someone to eat lunch at pgp? Second time',
    creator= HIEU,
    group=HIEU_GROUP
)

SON_COMMENT = Comment.objects.create_comment(
    content = 'OKAY',
    post_id = HIEU_POST,
    creator= SON
)
