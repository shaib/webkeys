from django.db import models
from django.db import transaction

class Layout(models.Model):
    name = models.CharField(max_length=64, unique=True)
    #num_levels = models.PositiveIntegerField(default=2)
    ref1 = models.ForeignKey("Level", null=True, related_name='ref1_using_layouts')
    ref2 = models.ForeignKey("Level", null=True, related_name='ref2_using_layouts')
    font = models.CharField(max_length=80, null=True, blank=True, default="verdana, ezra sil")
    
    def __unicode__(self):
        return "Layout: " + self.name
    
    @transaction.commit_on_success
    def clone(self, name):
        "Create a copy of me with a new name"
        clon = Layout.objects.create(name=name, ref1=self.ref1, ref2=self.ref2,
                                     font=self.font)
        for level in self.level_set.all():
            level.clone(clon)
        return clon
    
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
