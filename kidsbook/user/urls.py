from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook.user import views

urlpatterns = [
    # Get User's Info
    # path('all/', views.GetAllUser.as_view()),
    path('record_time/', views.RecordTime.as_view()),
    path('<uuid:pk>/', views.GetInfoUser.as_view()),
    path('setting/', views.SettingUser.as_view()),
    path('<uuid:pk>/groups/', views.GetGroups.as_view()),

    path('<uuid:pk>/posts/', views.GetPost.as_view()),
    path('login/', views.LogIn.as_view()),
    path('login_as_virtual/', views.LogInAsVirtual.as_view()),
    path('register/', views.Register.as_view()),
    path('virtual_users/', views.GetVirtualUsers.as_view()),
    path('logout/', views.LogOut.as_view()),

    path('update/<uuid:pk>/', views.Update.as_view()),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
