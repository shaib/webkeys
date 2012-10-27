'''
Utilities for the caps_options
(functions needed for defining caps-options easily)

Created on Jul 25, 2011

@author: shai
'''

# Key types for supporting caps lock behaviors

EIGHT_LEVEL = 'EIGHT_LEVEL'
SIX_LEVEL = 'SIX_LEVEL'
FOUR_LEVEL = 'FOUR_LEVEL_ALPHABETIC'
CAPS_KEY_TYPES = frozenset([EIGHT_LEVEL, SIX_LEVEL, FOUR_LEVEL])

options = {}

def caps_option(name, free_caps=True, key_type=None):
    def register(func):
        if name in options:
            new = func.func_name
            old = options[name].func_name
            raise IndexError("Name %s for function %s already used with %s" % (name, new, old))
        func.key_type = key_type
        func.free_caps = (not key_type) and free_caps
        options[name] = func
        return func
    return register

def get(name):
    return options[name] if name else Default

def _tooltip(name,func):
    if func.func_doc:
        text = func.func_doc.strip()
        return "<br/>".join(text.split("\n")) 
    else:
        return None

def _free_caps(func):
    return "true" if func.free_caps else ""

def choices():
    return tuple((name, func.func_name, _tooltip(name, func), _free_caps(func))
                  for name,func 
                  in sorted (options.items(),key=lambda kv:kv[1].func_name))

# This function's name is capitalized to make it first in the ordering.
@caps_option("Default", free_caps=False)
def Default(key): 
    "Caps lock behavior not specified by mapping"
    return None
