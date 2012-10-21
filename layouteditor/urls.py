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
    url(r'^show/(?P<owner>\w+)/(?P<name>\w+)/$', show_layout, name="show-layout"),
    url(r'^edit/(?P<owner>\w+)/(?P<name>\w+)/(?P<row>[0-4])/(?P<pos>1?\d)/$', edit_key, name="edit-key"),
    url(r'^undo/(?P<owner>\w+)/(?P<name>\w+)/$', undo_edit, name="undo-edit-key"),
    url(r'^redo/(?P<owner>\w+)/(?P<name>\w+)/$', redo_edit, name="redo-edit-key"),
    #url(r'^$', list_detail.object_list, layout_info, name="layouts"),
    url(r'^clone/(?P<owner>\w+)/(?P<name>\w+)/$', clone_layout, name="clone-layout"),
    url(r'^genxkb/(?P<owner>\w+)/(?P<name>\w+)/$', gen_xkb, name="gen-xkb"),
    url(r'^genklc/(?P<owner>\w+)/(?P<name>\w+)/$', gen_klc, name="gen-klc"),
    url(r'^genmap/(?P<owner>\w+)/(?P<name>\w+)/$', gen_map, name="gen-map"),
    

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
