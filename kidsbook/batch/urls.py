from django.urls import path
from kidsbook.batch import views

urlpatterns = [
    path('create/user/<filename>/', views.batch_create)
]
