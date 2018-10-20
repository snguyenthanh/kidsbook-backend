from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook import views
from django.conf.urls import include

urlpatterns = [
    path('user/', include('kidsbook.user.urls')),
    path('group/', include('kidsbook.group.urls')),
    path('batch/', include('kidsbook.batch.urls')),
    path('group/<uuid:pk>/posts/', views.GroupPostList.as_view()),
    path('post/<uuid:pk>/', views.PostDetail.as_view()),
    path('post/<uuid:pk>/complete', views.CompletePostDetail.as_view()),
    path('post/<uuid:pk>/likes', views.PostLike.as_view()),
    path('comment/<uuid:pk>/likes', views.CommentLike.as_view()),
    path('post/<uuid:pk>/shares', views.PostShare.as_view()),
    path('post/<uuid:pk>/comments', views.PostCommentList.as_view()),
    path('post/<uuid:pk>/flag', views.PostFlag.as_view()),
    path('comment/<uuid:pk>/', views.CommentDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)