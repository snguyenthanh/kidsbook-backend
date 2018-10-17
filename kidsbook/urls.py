from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook import views
from django.conf.urls import include

urlpatterns = [
    path('user/', include('kidsbook.user.urls')),
    path('post/', views.PostList.as_view()),
    path('posts/<uuid:pk>/', views.PostDetail.as_view()),
    path('comments/', views.CommentList.as_view()),
    path('comments/<uuid:pk>/', views.CommentDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
