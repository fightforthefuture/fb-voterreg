from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from main.views import OGObjectView


admin.autodiscover()

urlpatterns = patterns('',
    (r'', include("main.urls", namespace="main")),
    url(r'staticpages/(?P<page_name>.*)', "staticpages.views.index", name="staticpages"),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^rosetta/', include('rosetta.urls')),
    url(r'^share_pledge', OGObjectView.as_view(template_name='pledge/index.html'), name="pledge_object"),
    url(r'^share_vote', OGObjectView.as_view(template_name='vote/index.html'), name="vote_object"),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
