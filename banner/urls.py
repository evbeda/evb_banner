from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from .views import (
    BannerView,
    BannerDesignView,
    BannerDetailView,
    BannerNewEventsSelectedCreateView,
)


urlpatterns = [

    url(r'^new/$',
        BannerNewEventsSelectedCreateView.as_view(template_name='events.html'),
        name='banner_new',
        ),
    url(r'^(?P<pk>[0-9]+)/banner_detail/$',
        BannerDetailView.as_view(),
        name='banner_detail',
        ),
    url(r'^(?P<pk>[0-9]+)/banner_design/$',
        BannerDesignView.as_view(),
        name='banner_design',
        ),
]
