from django.urls import path
from kidsbook.notification import views

urlpatterns = [
    path('notifications/', views.notification)
]
