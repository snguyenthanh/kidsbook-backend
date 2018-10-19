from django.urls import path
from kidsbook.group import views

urlpatterns = [
    # Return all groups or create a new group
    path('', views.group),

    # Add new member or remove a member in a group
    path('<group_id>/user/<user_id>/', views.group_member),

    path('<group_id>/', views.delete_group)
]
