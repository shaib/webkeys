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

@caps_option("Default")
def default(key):
    "Caps lock behavior not specified by mapping"
    return None
