from django.conf.urls.defaults import *
from django.views.generic import list_detail

from models import Layout
from views import * 
from forms import CloneForm
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

layout_info = {
    "queryset" : Layout.objects.all(),
    "template_name" : "layout_list.html",
    "template_object_name" : "layout",
    "extra_context" : { "form" : CloneForm }
}


urlpatterns = patterns('',
    url(r'^show/$', show_layout),
    url(r'^show/(?P<name>\w+)/$', show_layout, name="show-layout"),
    url(r'^edit/$', edit_key),
    url(r'^edit/(?P<name>\w+)/(?P<row>[0-4])/(?P<pos>1?\d)/$', edit_key, name="edit-key"),
    url(r'^$', list_detail.object_list, layout_info, name="layouts"),
    url(r'^clone/(?P<name>\w+)/$', clone_layout, name="clone-layout"),
    url(r'^setfont/(?P<name>\w+)/$', set_layout_font, name="set-layout-font"),
    url(r'^genxkb/(?P<name>\w+)/$', gen_xkb, name="gen-xkb"),
    url(r'^genklc/(?P<name>\w+)/$', gen_klc, name="gen-klc"),
    url(r'^genmap/(?P<name>\w+)/$', gen_map, name="gen-map"),
    

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
