from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('pantry.accounts.views',
    url(r'^login/', 'login_page', name='login_page'),
    url(r'^logout/', 'logout_page', name='logout_page'),
)
