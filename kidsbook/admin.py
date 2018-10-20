from django.contrib import admin
from django.contrib.sessions.models import Session

# Register your models here.

from . import models


class UserModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username', 'email_address', 'is_superuser', 'is_staff', 'role']
    list_filter = ['is_superuser', 'is_staff']
    search_fields = ['pk', 'username', 'email_address']
    # filter_horizontal = ['groups', 'user_permissions', 'friends']
    filter_horizontal = ['groups']

class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']

class PostModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'content', 'creator']

class CommentModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'content', 'post', 'creator']

class GroupModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']

class GroupMemberModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'group']

admin.site.register(Session, SessionAdmin)
admin.site.register(models.User, UserModelAdmin)
admin.site.register(models.Post, PostModelAdmin)
admin.site.register(models.Comment, CommentModelAdmin)
admin.site.register(models.Group, GroupModelAdmin)
admin.site.register(models.GroupMember, GroupMemberModelAdmin)
