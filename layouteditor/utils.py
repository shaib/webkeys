# -*- coding: utf-8 -*-
'''
Created on Jan 20, 2011

@author: shai
'''
from django.db import transaction
from models import Layout, Level, KeyBinding


def make_level_keys(level, rows):
    assert len(rows)==5
    start = [0,1,1,1,3]
    for row,chars in enumerate(rows):
        offset = start[row]
        for pos,char in enumerate(chars):
            KeyBinding.objects.create(level=level,
                                      row=row,
                                      pos=pos+offset,
                                      char=char)
@transaction.commit_on_success
def make_qwerty():
    qwerty = Layout.objects.create(name="qwerty_ref", ref1=None, ref2=None)
    # Unshifted
    level = Level.objects.create(layout=qwerty, level=1)
    rows = ["`1234567890-=",
            "QWERTYUIOP[]\\",
            "ASDFGHJKL;'",
            "ZXCVBNM,./",
            " "]
    make_level_keys(level,rows)
    qwerty.ref1 = level
    # Shifted
    level = Level.objects.create(layout=qwerty, level=2, modifiers="shift")
    rows = ["~!@#$%^&*()_+",
            "QWERTYUIOP{}|",
            'ASDFGHJKL:"',
            "ZXCVBNM<>?",
            " "]
    make_level_keys(level,rows)
    qwerty.ref2 = level
    qwerty.save()

def make_key_binder(level):
    qwerty = Level.objects.get(layout__name='qwerty_ref', level=1)
    def bind_key(qwerty_char, char):
        qbind = KeyBinding.objects.get(level=qwerty, char=qwerty_char)
        KeyBinding.objects.create(level=level, char=char,
                                  row=qbind.row,
                                  pos=qbind.pos)
    return bind_key

def make_si1452():
    qwerty = Layout.objects.get(name="qwerty_ref")
    si1452 = Layout.objects.create(name="si1452", ref1=qwerty.ref1, ref2=qwerty.ref2)
    level = Level.objects.create(layout=si1452, level=1)
    rows = [";1234567890-=",
            u"/'קראטוןםפ[]\\",
            u"שדגכעיחלךף,",
            u"זסבהנמצתץ.",
            " "]
    make_level_keys(level,rows)
    level = Level.objects.create(layout=si1452, level=2)
    rows = ["~!@#$%^&*()_+",
            "QWERTYUIOP{}|",
            'ASDFGHJKL:"',
            "ZXCVBNM<>?",
            " "]
    make_level_keys(level,rows)
    more_si1452(si1452)
    
def more_si1452(si1452=None):
    if not si1452:
        si1452 = Layout.objects.get(name="si1452")
    level = Level.objects.create(layout=si1452, level=3)
    bind = make_key_binder(level)
    bind('Q',u'\u05c2') #SIN DOT
    bind('W',u'\u05c1') #SHIN DOT
    bind('3',u'\u20ac') #EURO
    bind('4',u'\u20aa') #SHEQEL
    bind(',',u'\u200f') #RLM
    bind('.',u'\u200e') #LRM
    bind('E',u'\u05b8') #QAMATS
    bind('-',u'\u05be') #MAQAF
    bind('U',u'\u05b9') #HOLAM
    level = Level.objects.create(layout=si1452, level=4)
    bind = make_key_binder(level)
    bind('E',u'\u05c7') #QAMATS QATAN
    bind('-',u'\u2013') #EN DASH
    bind('U',u'\u05ba') #HOLAM HASER FOR VAV
    bind('B',u'\u05c6') #NUN HAFUCHA
