from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include

urlpatterns = [
    path('user/', include('kidsbook.user.urls')),
    path('group/', include('kidsbook.group.urls')),
    path('batch/', include('kidsbook.batch.urls')),
    path('', include('kidsbook.post.urls')),
    path('users/', include('kidsbook.users.urls'))
]

urlpatterns = format_suffix_patterns(urlpatterns)
