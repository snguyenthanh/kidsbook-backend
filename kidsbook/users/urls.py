from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook.users import views

urlpatterns = [
    path('', views.users_allowed_to_be_discovered),
    path('non_group/', views.non_group)
]

# urlpatterns = format_suffix_patterns(urlpatterns)
