from django.contrib import admin
from django.contrib.sessions.models import Session

# Register your models here.
 
from . import models


class UserModelAdmin(admin.ModelAdmin):
    list_display = ['pk', 'username', 'email_address', 'is_superuser', 'is_staff']
    list_filter = ['is_superuser', 'is_staff']
    search_fields = ['pk', 'username', 'email_address']
    # filter_horizontal = ['groups', 'user_permissions', 'friends']

class SessionAdmin(admin.ModelAdmin):
    def _session_data(self, obj):
        return obj.get_decoded()
    list_display = ['session_key', '_session_data', 'expire_date']

admin.site.register(Session, SessionAdmin)
admin.site.register(models.User, UserModelAdmin)
