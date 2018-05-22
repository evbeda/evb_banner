from django.conf.urls import url
from .utils import accept_webhook
from .views import (
    AddUnassignedEventsView,
    BannerPreview,
    BannerNewEventsSelectedCreateView,
    BannerDeleteView,
    EditEventDesignView,
    SortInEvents,
    EditAllEventDesignView,
)
from . import views


urlpatterns = [

    url(r'^new/$',
        BannerNewEventsSelectedCreateView.as_view(
            template_name='event_list.html',
        ),
        name='banner_new',),
    url(r'^(?P<pk>[0-9]+)/preview/$',
        BannerPreview.as_view(),
        name='preview',),
    url(r'^(?P<pk>[0-9]+)/banner_delete/$',
        BannerDeleteView.as_view(),
        name='banner_delete',),
    url(r'^(?P<pk>[0-9]+)/banner_update/$',
        BannerNewEventsSelectedCreateView.as_view(
            template_name='event_list.html'
        ),
        name='banner_update'),
    url(r'^(?P<pk>[0-9]+)/event/(?P<epk>[0-9]+)/$',
        EditEventDesignView.as_view(),
        name='edit_design'),
    url(r'events/add/$',
        AddUnassignedEventsView.as_view(),
        name='add_events'),
    url(r'event/add',
        accept_webhook,
        name='accept_webhook',
        ),
    url(r'^(?P<pk>[0-9]+)/sort_in_events/$',
        SortInEvents.as_view(),
        name='order_in_events',
        ),
    url(r'^new/id$', views.get_api_event_by_id, name='banner_new_id'),
    url(r'^(?P<pk>[0-9]+)/eventdesign/$',
        EditAllEventDesignView.as_view(),
        name='edit_all_design'),
]
