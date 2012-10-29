# This Python file uses the following encoding: utf-8
'''
Created on Oct 29, 2012

@author: shai
'''

from django.test import TestCase
from django.contrib.auth.models import User
from models import Profile

class TestProfile(TestCase):
    
    def setUp(self):
        user = User.objects.create_user("alpha", "omega@example.com")
        prof = self.prof = user.get_profile()
        prof.name = "Aleph Efes"
        prof.website = "www.example.com"
        prof.location = "Example City"
        prof.affiliation = "Example Company"
        prof.save()
        
    def test_copyright(self):
        prof = self.prof
        prof.copyright_template = u'(c) %(year)s %(name)s (%(website)s, %(email)s)'
        c = prof.copyright(1995)
        self.assertEqual(c, u'(c) 1995 Aleph Efes (www.example.com, omega@example.com)')
        c = prof.copyright(1993,1995)
        self.assertEqual(c, u'(c) 1995 Aleph Efes (www.example.com, omega@example.com)')
        
        prof.copyright_template = u'(c) %(years)s %(affiliation)s of %(location)s'
        c = prof.copyright(1995)
        self.assertEqual(c, u'(c) 1995 Example Company of Example City')
        c = prof.copyright(1995,1995)
        self.assertEqual(c, u'(c) 1995 Example Company of Example City')
        c = prof.copyright(1993,1995)
        self.assertEqual(c, u'(c) 1993--1995 Example Company of Example City')
