from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

def url_about_template(name):
    regex = r"^%s/$" % name
    params = dict(template="about/%s.html" % name)
    return url(regex, direct_to_template, params, name=name)

urlpatterns = patterns("",
    url(r"^$", direct_to_template, {"template": "about/about.html"}, name="about"),
#    url(r"^terms/$", direct_to_template, {"template": "about/terms.html"}, name="terms"),
#    url(r"^privacy/$", direct_to_template, {"template": "about/privacy.html"}, name="privacy"),
#    url(r"^dmca/$", direct_to_template, {"template": "about/dmca.html"}, name="dmca"),
    url_about_template("what_next"),
    url_about_template("use_xkb"),
    url_about_template("use_klc"),
    url_about_template("downloads"),
)
