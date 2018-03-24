from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from .views import EventsView


urlpatterns = [

    url(r'^new/$', EventsView.as_view(template_name='events.html'),
        name='banner_new'),
]
