from django.urls import include, path

urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
]
