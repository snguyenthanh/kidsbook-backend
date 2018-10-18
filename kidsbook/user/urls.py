from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from kidsbook.user import views

urlpatterns = [
    # Get User's Info
    path('profile/', views.GetInfo.as_view()),
    path('<uuid:user_id>/', views.GetInfoUser.as_view()),
    
    path('posts/', views.GetPost.as_view()),
    path('login/', views.LogIn.as_view()),
    path('update/', views.Update.as_view()),
    path('register/', views.Register.as_view()),
    # path('batchCreate/', views.BatchCreate.as_view())
]

# urlpatterns = format_suffix_patterns(urlpatterns)
