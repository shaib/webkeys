from django.db import models
from django.db import transaction
from django.contrib.auth.models import User, SiteProfileNotAvailable
from django.db.models import permalink

DEFAULT_COPYRIGHT = u"This file is in the public domain" # TODO: Setting?

class Layout(models.Model):
    owner = models.ForeignKey(User)
    name = models.CharField(max_length=64)
    ref1 = models.ForeignKey("Level", null=True, related_name='ref1_using_layouts')
    ref2 = models.ForeignKey("Level", null=True, related_name='ref2_using_layouts')
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = (("owner", "name"),)
        
    def __unicode__(self):
        return "Layout: " + self.name
    
    @property
    def copyright(self):
        try:
            renderer = self.owner_profile().copyright
            start_year = self.created.year
            last_change = KeyChange.objects.to_undo(self)
            end_year = last_change and last_change.when.year
            return renderer(start_year, end_year)
        except:
            return DEFAULT_COPYRIGHT
    
    def owner_profile(self):
        try:
            return self.owner.get_profile()
        except SiteProfileNotAvailable:
            return FakeProfile(self.owner)
                
    @permalink
    def get_absolute_url(self):
        return ("show-layout", (self.owner.username, self.name))
        
    @transaction.commit_on_success
    def clone(self, owner, name):
        "Create a copy of me with a new name"
        clon = Layout.objects.create(owner=owner, name=name,
                                     ref1=self.ref1, ref2=self.ref2)
        for level in self.level_set.all():
            level.clone(clon)
        return clon
    
# Not a model -- just a helper for the Layout class 
class FakeProfile(object):
    def __init__(self, user):
        self.name = user.username
        self.affiliation = None
    def copyright(self, *args):
        return DEFAULT_COPYRIGHT
        
class Level(models.Model):
    layout = models.ForeignKey(Layout)
    level = models.PositiveIntegerField()
    modifiers = models.CharField(max_length=30, null=True, blank=True, default="") # TODO validation
    
    class Meta:
        unique_together = (("layout", "level"),)
    
    def __unicode__(self):
        return "/".join([unicode(self.layout),unicode(self.level)])

    @transaction.commit_on_success
    def clone(self, layout):
        "Create a copy of me under a new layout"
        clon = Level.objects.create(layout=layout, level=self.level, modifiers=self.modifiers)
        for kb in self.keybinding_set.all():
            kb.clone(clon)
        return clon

    
class KeyBinding(models.Model):
    level = models.ForeignKey(Level)
    row = models.PositiveIntegerField()
    pos = models.PositiveIntegerField()
    char = models.CharField(max_length=1)
    
    @property
    def mod_level(self):
        return self.level.level

    def __unicode__(self):
        what = "/".join([self.level.layout.name,
                         'l%d'%self.mod_level,
                         'r%d'%self.row,
                         str(self.pos)])
        return "Key: " + what + " = " + self.char
    
    def clone(self, level):
        "Create a copy of me under a new level"
        return KeyBinding.objects.create(level=level, row=self.row, pos=self.pos, char=self.char)

class KeyChangeManager(models.Manager):

    def to_undo(self, layout):
        try:
            return self.filter(layout=layout, done=True).latest()
        except KeyChange.DoesNotExist:
            return None
    
    def to_redo(self, layout):
        try:
            return self.filter(layout=layout, done=False).order_by('when')[0]
        except IndexError:
            return None

    def clear_redo_stack(self, layout):
        return self.filter(layout=layout, done=False).delete()
    
class KeyChange(models.Model):

    # Note: This differs from the above model, saving all 4 levels
    #       for one key in one string.
    #       This is far more efficient, a little less general, and probably
    #       the right way to go forward in this app.

    NULL = chr(0)
    EMPTY = 4*NULL

    layout = models.ForeignKey(Layout)
    row = models.PositiveIntegerField()
    pos = models.PositiveIntegerField()
    before = models.CharField(max_length=4)
    after = models.CharField(max_length=4)
    done = models.BooleanField(default=True)
    when = models.DateTimeField(auto_now_add=True)
    
    objects = KeyChangeManager()
    
    class Meta:
        get_latest_by = 'when'
        
    def __init__(self, *args, **kw):
        kw.setdefault('before', KeyChange.EMPTY)
        kw.setdefault('after', KeyChange.EMPTY)
        super(KeyChange, self).__init__(*args, **kw)

    def set_before(self, lvl, char):
        self.before = self.before[:lvl-1]+char+self.before[lvl:]
    def set_after(self, lvl, char):
        self.after = self.after[:lvl-1]+char+self.after[lvl:]
        
