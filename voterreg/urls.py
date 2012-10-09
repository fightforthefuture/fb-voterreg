from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = patterns('',
    (r'', include("main.urls", namespace="main")),
    url(r'staticpages/(?P<page_name>.*)', "staticpages.views.index", name="staticpages"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rosetta/', include('rosetta.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
