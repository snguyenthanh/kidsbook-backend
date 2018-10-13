from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook.user import views

urlpatterns = [
    path('', views.GetInfo.as_view()),
    path('posts/', views.GetPost.as_view())
]

# urlpatterns = format_suffix_patterns(urlpatterns)