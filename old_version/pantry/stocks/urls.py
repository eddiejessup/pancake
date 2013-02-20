from django.conf.urls.defaults import patterns, url
from pantry.stocks.views import StockCreate

urlpatterns = patterns('pantry.stocks.views',
    url(r'^home/$', 'home', name='home'),
    url(r'^search/(?P<barcode>\d+)/$', 'search', name='search_stock'),
    url(r'^lookup/(?P<barcode>\d+)/$', 'lookup', name='barcode_lookup'),
    url(r'^use/(?P<pk>\d+)/$', 'use', name='use_stock'),
#    url(r'^add/$', 'add', name='add_stock'),
    url(r'^add/$', StockCreate, name='add_stock'),
#    url(r'^addprod/$', 'add_product', name='add_product'),
    url(r'^addprodpacks/$', 'add_prodpacks', name='add_prodpacks'),
    url(r'^ajax_get_product/$', 'ajax_get_product'),
)
