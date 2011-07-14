'''
Created on Jul 5, 2011

@author: shai
'''

#
# Administrative area
#
# Here we define the mechanisms that make this file work
#
options = {}

def caps_option(name):
    def register(func):
        if name in options:
            new = func.func_name
            old = options[name].func_name
            raise IndexError("Name %s for function %s already used with %s" % (name, new, old))
        options[name] = func
        return func
    return register

def get(name):
    return options[name] if name else default

def _choice_text(name,func):
    if func.func_doc:
        desc = func.func_doc.split("\n",1)[0] 
        return "%s: %s" % (name, desc)
    else:
        return name
     
def choices():
    return tuple((name, _choice_text(name, func))
                  for name,func 
                  in options.iteritems())

__all__ = ['get', 'choices']
#
# Content area
#
# Here we define caps-lock policy functions
#
# Each function is presented by name (parameter to caps_lock decorator)
# and description (first line of doc)
import unicodedata as U
from keymaps import mirror

@caps_option("Default")
def default(key):
    "Caps lock behavior not specified by mapping"
    return None

@caps_option("Latin")
def latin(key):
    "Turn the keyboard to latin (US) in first two levels"
    return key.ref1.lower(), key.ref2.upper()

@caps_option("Mirrored Latin")
def mirrored_latin(key):
    "Turn the keyboard to latin (US) in first two levels, but apply mirroring"
    m = lambda u:mirror(u, True)
    return map (m, (key.ref1.lower(), key.ref2.upper()))

@caps_option("Capitals")
def capitals(key):
    "Make latin letter keys produce capitals, others unshifted US; with shift, Hebrew letters and otherwise shifted Hebrew."
    unshifted = key.ref1.upper()
    is_hebrew_letter = U.name(key.level_chars[1]).startswith('HEBREW LETTER')
    is_shifted_latin = key.level_chars[2].isalpha()
    shifted = key.level_chars[1] if (is_hebrew_letter or is_shifted_latin) else key.level_chars[2]
    return unshifted, shifted

@caps_option("Lock Level 3")
def lock3(key):
    "Lock level 3, shift produces level 4"
    return key.level_chars[3:]
