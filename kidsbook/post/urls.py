from django.urls import path
from kidsbook.post import views

urlpatterns = [
    path('group/<uuid:pk>/posts/', views.GroupPostList.as_view()),
    path('group/<uuid:pk>/flagged/', views.GroupFlaggedList.as_view()),
    path('post/<uuid:pk>/', views.PostDetail.as_view()),
    path('post/<uuid:pk>/likes/', views.PostLike.as_view()),
    path('post/<uuid:pk>/shares/', views.PostShare.as_view()),
    path('post/<uuid:pk>/comments/', views.PostCommentList.as_view()),
    path('post/<uuid:pk>/flags/', views.PostFlag.as_view()),
    path('comment/<uuid:pk>/', views.CommentDetail.as_view()),
    path('comment/<uuid:pk>/likes/', views.CommentLike.as_view()),
    path('comment/<uuid:pk>/flags/', views.CommentFlag.as_view())
]
