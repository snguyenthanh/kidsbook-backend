from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook import views

urlpatterns = [
    path('posts/', views.ActualPostList.as_view()),
    path('filtered-posts/', views.CensoredPostList.as_view()),
    path('posts/<int:pk>/', views.PostDetail.as_view()),
    path('comments/', views.CommentList.as_view()),
    path('comments/<int:pk>/', views.CommentDetail.as_view()),
    path('users/', views.UserList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)