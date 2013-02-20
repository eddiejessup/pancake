from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
#from pantry import settings
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/', include('pantry.accounts.urls')),
    url(r'^stocks/', include('pantry.stocks.urls')),
    url(r'^health/', include('pantry.health.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
)
print 'hi'