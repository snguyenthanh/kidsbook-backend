from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook import views
from django.conf.urls import include

urlpatterns = [
    path('user/', include('kidsbook.user.urls')),
    path('group/', include('kidsbook.group.urls')),
    path('group/<uuid:pk>/posts/', views.GroupPostList.as_view()),
    path('posts/<uuid:pk>/', views.PostDetail.as_view()),
    path('posts/<uuid:pk>/complete', views.CompletePostDetail.as_view()),
    path('posts/<uuid:pk>/like', views.PostLike.as_view()),
    path('posts/<uuid:pk>/share', views.PostShare.as_view()),
    path('posts/<uuid:pk>/comments', views.PostCommentList.as_view()),
    path('posts/<uuid:pk>/flag', views.PostFlag.as_view()),
    path('comments/<uuid:pk>/', views.CommentDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
