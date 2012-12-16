from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    
    
    # image api
    url(r'^api/v(?P<version>\d+)/(?P<module>[a-z]+)/(?P<method>[a-z]+)\.?(?P<format>[a-z]+)?', 'main.api_views.api_dispatcher'),
    
    
    # other stuff
    url(r'^convert-font', 'main.views.font_converter', name='font_converter'),
    url(r'^merge-fonts', 'main.views.font_merger', name='font_merger'),
    url(r'^get-favicon', 'main.views.favicon_getter', name='favicon_getter'),
    
    # troll service
    url(r'^troll-a-face', 'main.views.simple_page', kwargs={"template": "troll.html"}, name='troll_face'),
    
    # image api
    url(r'^api', 'main.views.simple_page', kwargs={"template": "image_api.html"}, name='image_api'),
    
    
    # TEST
    url(r'^pix.me/code', 'main.views.simple_page', kwargs={"template": "pixme_base.html"}),
    
    # last
    url(r'^$', 'main.views.simple_page', kwargs={"template": "troll.html"}),
    
    
    # Examples:
    # url(r'^$', 'imageapi.views.home', name='home'),
    # url(r'^imageapi/', include('imageapi.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    
)

urlpatterns += staticfiles_urlpatterns()

"""
    # TODO api/....
    url(r'^get-faces', 'main.views.face_getter', name='face_getter'),
    
    url(r'^faces', 'main.views.simple_page', kwargs={"template": "faces.html"}, name='faces'),
"""


"""                
    # TODO api/....
    url(r'placeholder.png', 'main.views.placeholder', name='placeholder'),
    #url(r'(?P<filename>.*)', 'main.views.image_serve', name='image_serve'),
    

"""