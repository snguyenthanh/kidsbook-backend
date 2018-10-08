from django.urls import path
from kidsbook import views

urlpatterns = [
    path('', views.post_list),
    path('<int:post_id>', views.post_detail),
]