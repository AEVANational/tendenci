from django.conf.urls.defaults import patterns, url
from martins_products.feeds import LatestEntriesFeed

urlpatterns = patterns('martins_products.views',                  
    url(r'^products/$', 'index', name="products"),
    url(r'^products/search/$', 'search', name="products.search"),
    url(r'^products/feed/$', LatestEntriesFeed(), name='products.feed'),
    url(r'^products/(?P<slug>[\w\-]+)/$', 'detail', name="products.detail"),
)
