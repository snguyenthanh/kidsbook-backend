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

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email_address, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email_address = self.normalize_email(email_address)
        user = self.model(username=username, email_address=email_address, **extra_fields)
        user.set_password(password)
        print("ABOUT TO SAVE")
        print(self._db)
        try:
            user.save(using=self._db)
            print("HIEU")
        except Exception as e:
            print(e)
        return user

    def create_user(self, username, email_address=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email_address, password, **extra_fields)

    def create_superuser(self, username, email_address, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email_address, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email_address = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    USERNAME_FIELD = 'email_address'
    EMAIL_FIELD = 'email_address'

    REQUIRED_FIELDS = ["username"]
    objects = UserManager()

class Post(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, blank=False)
    content = models.TextField(blank=False)
    owner = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)

    class Meta:
        ordering = ('created',)

class Comment(models.Model):
    text = models.CharField(max_length=100, blank=False)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
