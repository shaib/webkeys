from django.db import models
from django.utils.translation import ugettext_lazy as _

from idios.models import ProfileBase


class Profile(ProfileBase):
    name = models.CharField(_("name"), max_length=50, null=True, blank=True)
    about = models.TextField(_("about"), null=True, blank=True)
    location = models.CharField(_("location"), max_length=40, null=True, blank=True)
    website = models.URLField(_("website"), null=True, blank=True, verify_exists=False)
    affiliation = models.CharField(_("affiliation"), max_length=50, null=True, blank=True)
    copyright_template = models.CharField(_("copyright template"), max_length=100, null=True, blank=True,
                                          help_text=_("Copyright note to put in your layout files.\n" +
                                                      "You can use %(x)s to include field values.\n"+
                                                      "x can be name, location, website, affiliation, email, year or years.\n"+
                                                      "(year is the last year the layout was saved, years is first--last)."),
                                          default=u'This file is in the public domain.') # \ua9 for copyright

    def layouts(self):
        return self.user.layout_set.all()
    
    def copyright(self, start_year, end_year=None):
        names = ("name", "location", "website", "affiliation")
        args = dict((name, getattr(self, name)) for name in names)
        args['email'] = self.user.email
        if end_year is None: end_year=start_year
        args['year'] = unicode(end_year)
        if start_year==end_year:
            args['years'] = args['year'] 
        else:
            args['years'] = u'%s--%s' %(start_year, end_year)
        return self.copyright_template % args
