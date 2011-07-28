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

old_si1452_nikud = {
    u'`': u'\u05b0', # Sheva
    u'1': u'\u05b1', # H. Segol
    u'2': u'\u05b2', # H. Patah
    u'3': u'\u05b3', # H.  Qamats
    u'4': u'\u05b4', # Hiriq
    u'5': u'\u05b5', # Tsere
    u'6': u'\u05b6', # Segol
    u'7': u'\u05b7', # Patah
    u'8': u'\u05b8', # Qamats
    u'9': u'\u05c2', # Sin dot
    u'0': u'\u05c1', # Shin dot
    u'-': u'\u05b9', # Holam
    u'=': u'\u05bc', # Dagesh/Shuruq

    u'\\': u'\u05bb', # Qubuts
}

@caps_option("SI1452")
def SI1452(key):
    """
    The SI1452 draft recommendation:
    Unshifted - like a US keyboard with CAPS locked
    Shifted - like level 1, except the top row gets the old-standard nikud
    """
    ref_char = key.ref_chars[1]
    unshifted = ref_char.upper()
    try:
        shifted = old_si1452_nikud[ref_char]
    except KeyError:
        shifted = key.level_chars[1]
    return unshifted, shifted

@caps_option("Caps Latin")
def caps_latin(key):
    "Act like a US keyboard with caps lock"
    # That is, take keys from ref levels 1 and 2,
    # and apply inverse capitalization
    return key.ref_chars[1].upper(), key.ref_chars[2].lower()
    
