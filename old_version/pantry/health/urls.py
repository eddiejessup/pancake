from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('pantry.health.views',
    url(r'^$', 'home', name='health_home'),
    url(r'^activity_log/$', 'activity_log_home', name='activity_log_home'),
    url(r'^activity_log/add/$', 'activity_log_add', name='activity_log_add'),
    url(r'^ajax_get_exercise/$', 'ajax_get_exercise'),
)