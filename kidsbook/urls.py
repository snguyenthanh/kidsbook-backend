from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook import views
from django.conf.urls import include

urlpatterns = [
    path('user/', include('kidsbook.user.urls')),
    path('group/', include('kidsbook.group.urls')),
    path('group/<uuid:group_id>/posts/', views.GroupPostList.as_view()),
    path('post/<uuid:post_id>/', views.PostDetail.as_view()),
    path('post/<uuid:post_id>/complete', views.CompletePostDetail.as_view()),
    path('post/<uuid:post_id>/likes', views.PostLike.as_view()),
    path('post/<uuid:post_id>/shares', views.PostShare.as_view()),
    path('post/<uuid:post_id>/comments', views.PostCommentList.as_view()),
    path('post/<uuid:post_id>/flag', views.PostFlag.as_view()),
    path('comment/<uuid:comment_id>/', views.CommentDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
