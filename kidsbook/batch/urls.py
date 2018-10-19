from django.urls import path
from kidsbook.batch import views

urlpatterns = [

    # This URL is for Testing only, as the APITestCase Client requires a <filename> URL keyword
    path('create/user/<filename>/', views.batch_create),

    path('create/user/', views.batch_create)
]
