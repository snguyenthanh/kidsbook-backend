from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
import uuid
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.hashers import make_password

class Role(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True)
    name = models.CharField(max_length=100)

# Create your models here.
class UserManager(BaseUserManager):
    # use_in_migrations = True

    def create_roles(self):
        role1 = Role(id=0, name='student')
        role2 = Role(id=1, name='teacher')
        role1.save()
        role2.save()

    def _create_user(self, username, email_address, password, role, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        self.create_roles()
        if not username:
            raise ValueError('The given username must be set')
        email_address = self.normalize_email(email_address)
        user = self.model(username=username, email_address=email_address, **extra_fields)
        user.role = Role(id=role)
        user.set_password(password)
        print("ABOUT TO SAVE")
        print(self._db)
        try:
            user.save(using=self._db)
            print("HIEU")
        except Exception as e:
            print(e)
        return user

    def create_user(self, username, email_address=None, password=None, role=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email_address, password, role, **extra_fields)

    def create_superuser(self, username, email_address, password, role, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email_address, password, role, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_address = models.EmailField(max_length=255, unique=True, editable=False)
    username = models.CharField(max_length=50, unique=True)
    realname = models.CharField(max_length=50)
    password = models.CharField(max_length=65530)
    gender = models.NullBooleanField()
    description = models.TextField(default="")
    date_of_birth = models.DateField(null=True)
    avatar_url = models.CharField(max_length=65530, null=True)
    login_time = models.PositiveIntegerField(default=0)
    screen_time = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    # role_id = models.ForeignKey(Role, related_name='post_owner', on_delete=models.CASCADE)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    USERNAME_FIELD = 'email_address'
    EMAIL_FIELD = 'email_address'

    REQUIRED_FIELDS = ["username", "password", "is_active", "realname"]
    role = models.ForeignKey(Role, related_name='group_owner', on_delete=models.CASCADE)
    objects = UserManager()

    def check_password(self, raw_password):
        print("REACH")
        print(make_password(raw_password))
        print(self.password)
        if self.password == raw_password:
            return True
        else:
            return False


class FakeStudent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_id = models.ForeignKey(User, related_name='student_id', on_delete=models.CASCADE)
    teacher_id = models.ForeignKey(User, related_name='teacher_id', on_delete=models.CASCADE)

class GroupManager(models.Manager):
    def create_group(self, name, creator):
        group = self.model(name=name)
        group.creator = creator
        group.save(using=self._db)
        group.add_member(creator)
        return group

class Group(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    description = models.TextField(null=True)
    creator = models.ForeignKey(User, related_name='group_owner', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='group_users', through='GroupMember')

    REQUIRED_FIELDS = ["name"]
    objects = GroupManager()

    def add_member(self, user):
        group_member = GroupMember(group=self, user_id=user)
        group_member.save()


class GroupMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class PostManager(models.Manager):
    #def create_post(self, title, content, creator):
    def create_post(self, **kargs):
        post = self.model(**kargs)
        post.save(using=self._db)
        return post

class Post(models.Model):
    # use_in_migrations = True
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    creator = models.ForeignKey(User, related_name='post_owner', on_delete=models.CASCADE, default=uuid.uuid4)
    likes = models.ManyToManyField(User, related_name='likes', through='UserLikePost')
    shares = models.ManyToManyField(User, related_name='shares', through='UserSharePost')

    REQUIRED_FIELDS = ["content"]

    objects = PostManager()
    class Meta:
        ordering = ('created_at',)

class UserLikePost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)

class UserSharePost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)


class CommentManager(models.Manager):
    def create_comment(self, **kargs):
        comment = self.model(**kargs)
        comment.save(using=self._db)
        return comment

class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    post_id = models.ForeignKey(Post, related_name='comments_post', on_delete=models.CASCADE, default=uuid.uuid4)
    creator = models.ForeignKey(User, related_name='comment_owner', on_delete=models.CASCADE, default=uuid.uuid4)

    REQUIRED_FIELDS = ['content']

    # use_in_migrations = True
    objects = CommentManager()
