from django.urls import path
from kidsbook.post import views

urlpatterns = [
    path('group/<uuid:group_id>/posts/', views.GroupPostList.as_view()),

    path('post/<uuid:post_id>/', views.PostDetail.as_view()),
    path('post/<uuid:post_id>/complete/', views.CompletePostDetail.as_view()),
    path('post/<uuid:post_id>/likes/', views.PostLike.as_view()),
    path('post/<uuid:post_id>/shares/', views.PostShare.as_view()),
    path('post/<uuid:post_id>/comments/', views.PostCommentList.as_view()),
    path('post/<uuid:post_id>/flag/', views.PostFlag.as_view()),

    path('comment/<uuid:comment_id>/', views.CommentDetail.as_view()),
    path('comment/<uuid:comment_id>/likes/', views.CommentLike.as_view()),
]
