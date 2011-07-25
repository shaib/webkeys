'''
Created on Jul 5, 2011

@author: shai
'''
#
# Here we define caps-lock policy functions
#
# Each function is presented by name (parameter to caps_lock decorator)
# and description (first line of doc)
#
# Each function takes a views.Key object, and is supposed to return a pair 
# (as list, tuple or other iterable) of characters to be used when caps is
# locked (the second character is for the case that shift is also pressed).
# The Key object has many properties and methods, but for these functions,
# the important ones are refs_chars and levels_chars. Both of these are lists
# of the characters produced by the key's reference levels (1,2) and mapping
# levels (1-4). Note that to make things more readable here, the index is
# 1-oriented and not 0-oriented as usual in Python.
# 
# In the resulting control, functions are ordered by their name; the default
# (no caps) function is named with a capital D to be first. Please keep
# function names all lower-case to preserve this.
# 
import unicodedata as U
from keymaps import mirror
from caps_options_utils import caps_option

@caps_option("Latin")
def latin(key):
    "Turn the keyboard to latin (US) in first two levels"
    return key.ref_chars[1:]

@caps_option("Mirrored Latin")
def latin_mirrored(key):
    """
    Turn the keyboard to latin (US) in first two levels, 
    but apply mirroring to restore latin-like behavior
    (useful for a layout with mirroring)
    """
    return [mirror(u, True) for u in key.ref_chars[1:]] 

@caps_option("Capitals")
def capitals(key):
    """
    Latin letter keys produce capitals, others unshifted US; 
    with shift, Hebrew letters are Hebrew, others are shifted Hebrew.
    """
    unshifted = key.ref_chars[1].upper()
    is_hebrew_letter = U.name(key.level_chars[1]).startswith('HEBREW LETTER')
    is_shifted_latin = key.level_chars[2].isalpha()
    shifted = key.level_chars[1] if (is_hebrew_letter or is_shifted_latin) else key.level_chars[2]
    return unshifted, shifted

@caps_option("Lock Level 3")
def lock3(key):
    "Lock level 3, shift produces level 4"
    return key.level_chars[3:]
