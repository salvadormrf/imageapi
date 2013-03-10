from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import settings
from mgmt.main.views import PageListView, PageDetailView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # admin
    (r'^admin/', include(admin.site.urls) ),
    
    # image api
    url(r'^api/v(?P<version>\d+)/(?P<module>[a-z]+)/(?P<method>[a-z]+)\.?(?P<format>[a-z]+)?', 'main.api_views.api_dispatcher'),
    
    # placeholders
    url(r'^page/(?P<pk>\d+)/$', PageDetailView.as_view(), name="page_detail"),
    url(r'^pages', PageListView.as_view(), name="page_list"),
    
    url(r'^$', PageListView.as_view(), name="page_list"),
)

urlpatterns += staticfiles_urlpatterns()














"""
# other stuff
url(r'^convert-font', 'main.views.font_converter', name='font_converter'),
url(r'^merge-fonts', 'main.views.font_merger', name='font_merger'),
url(r'^get-favicon', 'main.views.favicon_getter', name='favicon_getter'),

# troll service
url(r'^troll-a-face', 'main.views.simple_page', kwargs={"template": "troll.html"}, name='troll_face'),

# image api
url(r'^api', 'main.views.simple_page', kwargs={"template": "image_api.html"}, name='image_api'),

# last
url(r'^$', 'main.views.simple_page', kwargs={"template": "troll.html"}),
"""