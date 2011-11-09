from django.conf.urls.defaults import *
from django.conf import settings

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
if settings.DEBUG:
    media_for_match = settings.MEDIA_URL
    # Patchy, wrong, doesn't deal with urls including protocol etc.
    if media_for_match[0]=='/': media_for_match = media_for_match[1:]
    if media_for_match[-1]=='/': media_for_match = media_for_match[:-1]
    static_url = r'^%s/(?P<path>.*)$' % media_for_match
    urlpatterns += patterns('',
        (static_url, 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
