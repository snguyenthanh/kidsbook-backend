from __future__ import unicode_literals

import uuid
import bcrypt
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import make_password

def format_value(value):
    if isinstance(value, list) and len(value) == 1:
        return value[0]
    return value

class Role(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

# Create your models here.
class UserManager(BaseUserManager):
    # use_in_migrations = True

    def create_roles(self):
        role1 = Role(id=1, name='teacher')
        role2 = Role(id=2, name='student')
        role3 = Role(id=3, name='Virtual student')
        role1.save()
        role2.save()
        role3.save()

    #def _create_user(self, username, email_address, password, role, **extra_fields):
    def _create_user(self, **kargs):
        """
        Creates and saves a User with the given username, email and password.
        """
        self.create_roles()
        if 'username' not in kargs:
            raise ValueError('The given username must be set')
            # kargs['username'] = 'anonymous'

        role = kargs.pop('role', 2)
        password = kargs.pop('password', '12345')

        #email_address = self.normalize_email(kargs['email_address'])
        kargs['email_address'] = self.normalize_email(kargs['email_address'])
        user = self.model(**kargs)

        user.role = Role(id=role)
        user.set_password(password)

        # if(kargs['teacher_id']):
        #     teacher = User.objects.get(id=kargs['teacher_id'])
        #     user.teacher = teacher

        #print("ABOUT TO SAVE")
        #print(self._db)
        try:
            user.save(using=self._db)
            #print("HIEU")
        except Exception as e:
            print(e)
        return user

    def create_user(self, **kargs):
        if 'is_staff' not in kargs:
            kargs['is_staff'] = False
        if 'is_superuser' not in kargs:
            kargs['is_superuser'] = False

        # kargs.setdefault('is_virtual_user', False)
        return self._create_user(role=2, **kargs)

    def create_virtual_user(self, **kargs):
        if 'is_staff' not in kargs:
            kargs['is_staff'] = True
        if 'is_superuser' not in kargs:
            kargs['is_superuser'] = False

        # kargs.setdefault('is_superuser', False)
        return self._create_user(role=3, **kargs)


    def create_superuser(self, **kargs):
        if 'is_staff' not in kargs:
            kargs['is_staff'] = True
        if 'is_superuser' not in kargs:
            kargs['is_superuser'] = True

        return self._create_user(role=1, **kargs)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_address = models.EmailField(max_length=255, unique=True, editable=False)
    username = models.CharField(max_length=50, unique=True)
    realname = models.CharField(max_length=50)
    password = models.CharField(max_length=65530)
    gender = models.BooleanField(default=False)
    description = models.TextField(default="")
    date_of_birth = models.DateField(null=True)
    #avatar_url = models.CharField(max_length=65530, null=True)
    profile_photo = models.ImageField(null=True)
    login_time = models.PositiveIntegerField(default=0)
    screen_time = models.PositiveIntegerField(default=0)

    teacher = models.ForeignKey('self', related_name='teacher_in_chage', on_delete=models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)
    # role_id = models.ForeignKey(Role, related_name='post_owner', on_delete=models.CASCADE, default=0)
    role = models.ForeignKey(Role, related_name='group_owner', on_delete=models.CASCADE)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    USERNAME_FIELD = 'email_address'
    EMAIL_FIELD = 'email_address'

    REQUIRED_FIELDS = ["username", "password", "is_active", "realname"]
    objects = UserManager()

    # def check_password(self, raw_password):
    #     print(self.password)
    #     print(make_password(raw_password))
    #     if self.password == make_password(raw_password):
    #         return True
    #     else:
    #         return False

class BlackListedToken(models.Model):
    token = models.CharField(max_length=500)
    user = models.ForeignKey(User, related_name="token_user", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("token", "user")

# class FakeStudent(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     student = models.ForeignKey(User, related_name='student', on_delete=models.CASCADE)
#     teacher = models.ForeignKey(User, related_name='teacher', on_delete=models.CASCADE)

class GroupManager(models.Manager):
    #def create_group(self, name, creator):
    def create_group(self, **kargs):
        # The arguments passed formats the `value` in <list>, need to extract them
        kargs = {key: format_value(value) for key,value in iter(kargs.items())}

        creator = kargs.pop('creator', None)
        if creator is None:
            raise ValueError('creator is missing.')

        group = self.model(**kargs)
        group.creator = creator
        group.save(using=self._db)
        group.add_member(creator)
        return group

class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    picture = models.ImageField(null=True)
    creator = models.ForeignKey(User, related_name='group_owner', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='group_users', through='GroupMember')

    REQUIRED_FIELDS = ["name"]
    objects = GroupManager()

    def add_member(self, user):
        group_member = GroupMember(group=self, user=user)
        group_member.save()


class GroupMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('user', 'group')


# class PostManager(models.Manager):
#     #def create_post(self, title, content, creator):
#     def create_post(self, **kargs):
#         post = self.model(**kargs)
#         post.save(using=self._db)
#         return post

class PostManager(models.Manager):
    def create_post(self, **kargs):
        post = self.model(**kargs)
        post.save(using=self._db)
        return post

class Post(models.Model):
    # use_in_migrations = True
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    objects = PostManager()
    creator = models.ForeignKey(User, related_name='post_owner', on_delete=models.CASCADE, default=uuid.uuid4)
    group = models.ForeignKey(Group, related_name='post_group', on_delete=models.CASCADE, default=uuid.uuid4)
    likes = models.ManyToManyField(User, related_name='likes', through='UserLikePost')
    shares = models.ManyToManyField(User, related_name='shares', through='UserSharePost')
    picture = models.ImageField(null=True)
    link = models.URLField(null=True)
    ogp = models.TextField(null=True)

    REQUIRED_FIELDS = ["content"]

    objects = PostManager()
    class Meta:
        ordering = ('created_at',)

class UserLikePost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    like_or_dislike = models.BooleanField(default=True)

class UserSharePost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

# class CommentManager(models.Manager):
#     def create_comment(self, **kargs):
#         comment = self.model(**kargs)
#         comment.save(using=self._db)
#         return comment

class CommentManager(models.Manager):
    def create_comment(self, **kargs):
        comment = self.model(**kargs)
        comment.save(using=self._db)
        return comment

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    post = models.ForeignKey(Post, related_name='comments_post', on_delete=models.CASCADE, default=uuid.uuid4)
    creator = models.ForeignKey(User, related_name='comment_owner', on_delete=models.CASCADE, default=uuid.uuid4)

    REQUIRED_FIELDS = ['post', 'creator', 'content']

    # use_in_migrations = True
    # objects = CommentManager()
    objects = CommentManager()

class UserLikeComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    like_or_dislike = models.BooleanField()
    class Meta:
        unique_together = ["user", "comment"]

class UserFlagPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=120, unique=True)
