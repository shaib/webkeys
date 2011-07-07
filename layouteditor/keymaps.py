'''
Created on Mar 4, 2011

@author: shai
'''
from unicodedata import name as char_name

from django.utils.safestring import mark_safe

XKB_MIRROR_COMMENT = mark_safe("// The following characters are mirrored: (), {}, [] and <>")
KLC_MIRROR_COMMENT = XKB_MIRROR_COMMENT
MIRRORS = {
 '(':')', ')':'(',
 '[':']', ']':'[',
 '{':'}', '}':'{',
 '<':'>', '>':'<',
}



def mirror(u, mirrored):
    if mirrored:
        # TODO: use http://www.unicode.org/Public/UNIDATA/BidiMirroring.txt
        # TODO: or even unicodedata.mirrored (which just says yes/no)        
        return unicode(MIRRORS.get(u, u))
    
    return u

def xkb(u, mirrored=False):
    "Turn value returned by presentation above into string for xkb"
    if not u:
        return "empty"
    c = mirror(u, mirrored)
    if 32 < ord(c) < 128 and c.isalnum():
        return c
    else:
        return "U%04X" % ord(c)
    
def xkb_comment(u, mirrored=False):
    if not u:
        return ""
    c = mirror(u, mirrored)
    if 32 < ord(c) < 128 and c.isalnum():
        return c
    mir = " (mirrored)" if c!=u else ""
    return char_name(c)+mir

def klc(u, mirrored=False):
    "Turn value returned by presentation above into string for klc"
    if not u:
        return "-1"
    c = mirror(u, mirrored)
    if 32 < ord(c) < 128 and c.isalnum() and c!='_':
        return c
    else:
        return "%04x" % ord(c)

def klc_comment(u, mirrored=False,
                none=mark_safe("<none>")):
    if not u:
        return none
    c = mirror(u, mirrored)
    mir = " (mirrored)" if c!=u else ""
    return char_name(c)+mir

def klc_sc(row, pos):
    if row==0 and pos>0:
        value = pos+1
    elif row==pos==0:
        value = 0x29
    elif row==1 and pos<13:
        value = pos + 0xf
    elif row==1 and pos==13:
        value = 0x2b
    elif row==2:
        value = pos + 0x1d
    elif row==3:
        value = pos + 0x2b
    elif row==4:
        value = 0x39 # just the space bar
    else:
        raise IndexError("row and pos don't designate a key on the keyboard")
    return '%02x' % value

KLC_VK_NAMES = {
    '-': 'OEM_MINUS',
    '=': 'OEM_PLUS',
    '[': 'OEM_4',
    ']': 'OEM_6',
    ';': 'OEM_1',
    "'": 'OEM_7',
    '`': 'OEM_3',
    "\\": 'OEM_5',
    ",": 'OEM_COMMA',
    '.': 'OEM_PERIOD',
    '/': 'OEM_2',
    ' ': 'SPACE'
}

def klc_vk(qwerty_char):
    if qwerty_char.isalnum():
        vk = qwerty_char
    else:
        vk = KLC_VK_NAMES[qwerty_char]
    if len(vk)<8: vk += "\t"
    return vk

def klc_cap(has_caps):
    return 'SGCap' if has_caps else '0'
    
    
def klc_special(qwerty_char):
    return klc(qwerty_char, False), klc_comment(qwerty_char, False)
