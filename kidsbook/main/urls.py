from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^api/', include('main.api.urls')),

    url(r'^$', views.display_index),

    url(r'^form/$', views.display_form),

]
