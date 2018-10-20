from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook.user import views

urlpatterns = [
    # Get User's Info
    # path('all/', views.GetAllUser.as_view()),
    path('profile/', views.GetInfo.as_view()),
    path('<uuid:pk>/profile/', views.GetInfoUser.as_view()),
    # path('<uuid:user_id>/group/', views.GetGroups.as_view()),

    path('posts/', views.GetPost.as_view()),
    path('login/', views.LogIn.as_view()),
    # path('loginAs/', views.LogInAs.as_view()),
    path('update/', views.Update.as_view()),
    path('register/', views.Register.as_view()),
    path('virtual_users/', views.GetVirtualUser.as_view()),
    path('logout/', views.LogOut.as_view())
]

# urlpatterns = format_suffix_patterns(urlpatterns)
