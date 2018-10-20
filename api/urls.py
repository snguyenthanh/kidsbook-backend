from django.urls import include, path

urlpatterns = [
    # path('api-auth/', include('rest_auth.urls')),
    # path('api-auth/', include('rest_auth.registration.urls')),
    path('', include('kidsbook.urls')),
]
