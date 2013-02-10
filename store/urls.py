from django.conf.urls import patterns, url
from store.views import *
from store.models import Product, Package, Stock

urlpatterns = patterns('store.views',
    url(r'^$', 'home', name='home'),

    url(r'^products/$', ProductList.as_view(), name='product-list'),
    url(r'^products/(?P<pk>\d+)/$', ProductDetail.as_view(), name='product-detail'),
    url(r'^products/new/$', product_update, name='product-add'),
    url(r'^products/update/(?P<pk>\d+)/$', product_update, name='product-update'),
    url(r'^products/search/barcode/$', ProductSearchBarcode.as_view(), name='product-search-barcode'),

    url(r'^products/lookup/$', ProductLookup.as_view(), name='product-lookup'),
#    url(r'^products/new_from_lookup/$', product_create_from_lookup, name='product-add-lookup'),

    url(r'^stocks/$', StockList.as_view(), name='stock-list'),
    url(r'^stocks/(?P<pk>\d+)/$', StockDetail.as_view(), name='stock-detail'),
    url(r'^stocks/new/$', StockCreate.as_view(), name='stock-add'),
    url(r'^stocks/update/(?P<pk>\d+)/$', StockUpdate.as_view(), name='stock-update'),
    url(r'^stocks/search/barcode/$', StockSearchBarcode.as_view(), name='stock-search-barcode'),
)
