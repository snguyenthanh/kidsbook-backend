from django.urls import include, path

urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
    path('post/', include('kidsbook.urls')),
]
