from django.urls import path
from kidsbook.group import views

urlpatterns = [
    # Return all groups or create a new group
    path('', views.group),

    # Add new member or remove a member in a group
    path('<uuid:pk>/user/<uuid:user_id>/', views.group_member),

    # View all members public profile of this group
    path('<uuid:pk>/user/', views.get_all_members_in_group),

    path('<uuid:pk>/', views.delete_group),

    # path('<group_id')
]
