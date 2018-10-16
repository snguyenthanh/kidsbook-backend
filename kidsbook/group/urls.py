from django.urls import include, path
from kidsbook.group import views

urlpatterns = [
    #path('api-auth/', include('rest_auth.urls')),
    path('', views.get_groups)
]
