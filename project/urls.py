from django.conf.urls.defaults import *  # @UnusedWildImport

#import layouteditor
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from django.contrib.auth.views import logout

urlpatterns = patterns('',
    # Example:
    # (r'^webkeys/', include('webkeys.foo.urls')),
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^signout/$', logout, kwargs={'next_page':'/'}, name='signout'),
    
    url(r'', include('layouteditor.urls')),
    

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
