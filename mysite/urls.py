from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf import settings
from django.conf.urls.static import static
from banner.views import BannerView
# from banner.views import create_webhook

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', BannerView.as_view(template_name='index.html'), name='index'),
    # url(r'^$', create_webhook, name='webhook'),
    url(r'^banner/', include('banner.urls')),
    url('', include('social_django.urls', namespace='social')),
    url(r'^accounts/login/$', login, name='login'),
    url(r'^accounts/logout/$', logout, name='logout'),
    url(r'^password_reset/$', login, name='password_reset'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
