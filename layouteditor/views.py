import re
from unicodedata import category, name as char_name

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db import transaction
from django.http import Http404, HttpResponseBadRequest
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
#from django.utils.html import escape as html_escape

from models import KeyBinding, Layout, Level
from forms import KeyForm, CloneForm, FontForm
import keymaps as km
import caps_options_utils as caps
import caps_options # just to load the options;  @UnusedImport


__all__ = ["show_layout",
           "set_layout_font", "edit_key",
           "clone_layout",
           "gen_xkb", "gen_klc", "gen_map"
]
                               


NBSP = u"&nbsp;"
ERASE_LEFT = u"&#x232B;"
RETURN = u"&#x23CE;"
YIN_YANG = u"&#x262F;"
UP_WHITE_ARROW = u"&#x21E7;"
BASE_KEY_WIDTH = 3.8
KEY_MARGIN = 0.1
KEY_BORDER = 0.3

SHIN_DOTS = u'\u05c1\u05c2'
HATAFIM = u'\u05b1\u05b2\u05b3'
HOLAM_HASER_FOR_VAV = u'\u05ba'

LRM,RLM = u'\u200e\u200f'
ZWNJ,ZWJ,CGJ=u'\u200c\u200d\u034f'

NONSPACING_MARK = "Mn" # unicode category
HTML_ALEPH = u'&#x05d0;'
HTML_VAV = u'&#x05d5;'
HTML_MEM = u'&#x05de;'
HTML_SHIN = u'&#x05e9;'

VISIBLE_FORMATTING = {
    LRM : '&#x21aa;', # RIGHTWARDS ARROW WITH HOOK
    RLM : '&#x21a9;', # LEFTWARDS ARROW WITH HOOK
    ZWJ : '&#x2194;', # LEFT RIGHT ARROW
    ZWNJ: '&#x21ae;', # LEFT RIGHT ARROW WITH STROKE
    CGJ : '&#x21ad;', # LEFT RIGHT WAVE ARROW
}

def is_one_char(s, 
                html_entity_re=re.compile(r'&#x[0-9A-Fa-f]{4};|&\w+;')):
    return len(s)==1 or html_entity_re.match(s)


class BaseKey(object):
    @property
    def style_width(self):
        return "%.2fem" % (self.width*BASE_KEY_WIDTH)
    

class FunctionKey(BaseKey):
    def __init__(self, name, width, **style):
        self.name=name
        self.width=width
        self.style={}
        if is_one_char(name):
            self.style['font-size']='200%'
        for k,v in style.items():
            self.style[k.replace("_","-")]=v
    @property
    def special_style(self):
        return "".join(["%s: %s;"%(key,val) for (key,val) in self.style.items()]) 
    
class StyleStr(unicode):
    @property
    def html(self):
        if hasattr(self, 'style'):
            return '<span class="%s">%s</span>' % (self.style, self)
        return self 
        
class Key(BaseKey):
    
    def __init__(self, ref1=None, ref2=None, width=1):
        self.width=width
        self.ref1=ref1
        self.ref2=ref2
        self.levels=[]
        self.styles=[]
    @property
    def levels1(self):
        return self.levels[1:]
    @property
    def refs(self):
        if self.ref1==self.ref2:
            return {self.ref1 : 'kbref1and2'}
        else:
            return {self.ref1 : 'kbref1', self.ref2 : 'kbref2'}
        
    def __setitem__(self, lvl, value):
        if lvl>=len(self.levels):
            # make sure the list is almost long enough
            extension = [None for _ in range(len(self.levels), lvl)]
            self.levels.extend(extension)
            self.levels.append(value)
        else:
            self.levels[lvl]=value
    def __getitem__(self, lvl):
        value = self.levels[lvl]
        if value is None:
            raise IndexError("Key not bound at level "+str(lvl))
        return value
    
    def xkb_chars(self):
        levels = [u.char if u else u for u in self.levels1]
        if self.caps_keys:
            levels.extend([None]*(4-len(levels)))
            levels += self.caps_keys
        return [km.xkb(u, self.mirrored) for u in levels]

    def xkb_comments(self):
        levels = [u.char if u else u for u in self.levels1]
        if self.caps_keys:
            levels += self.caps_keys
        return filter(None, [km.xkb_comment(u, self.mirrored) for u in levels])

    def klc_chars(self):
        levels = [u.char if u else u for u in self.levels1]
        return [km.klc(u, self.mirrored) for u in levels]

    def klc_comments(self):
        levels = (u.char if u else u for u in self.levels1)
        return [km.klc_comment(u, self.mirrored) for u in levels]

    def klc_caps_chars(self):
        return [km.klc(u, self.mirrored) for u in self.caps_keys]
    
    def klc_caps_comments(self):
        return [km.klc_comment(u, self.mirrored) for u in self.caps_keys]
    
    def klc_annotate(self, row, pos):
        self.sc = km.klc_sc(row, pos)
        self.vk = km.klc_vk(self.ref1)        
        self.cap = km.klc_cap(bool(self.caps_keys))
        levels = self.levels
        if len(levels)<5:
            levels[len(levels):5]=(5-len(levels))*[None]
        levels[3:3] = [None]
        
    @property
    def level_chars(self):
        "For use in caps options. Returns the chars of the levels, with level 1 at index 1"
        # Note: the above similar lines use self.levels1, where level 1 is at index 0.
        return [u.char if u else u for u in self.levels]
    
    @property
    def ref_chars(self):
        """
        For use in caps options. Returns the chars of the reference levels, with level 1 at index 1.
        Makes caps_options functions cleaner, because it hides the little caps ugliness in the
        reference levels.
        """
        return (None, self.ref1.lower(), self.ref2.upper())

    
def kb105():
    compensate = (KEY_MARGIN+2*KEY_BORDER)/BASE_KEY_WIDTH
    F = FunctionKey
    row0 = [Key() for _ in range(13)] + [F(ERASE_LEFT, 2.)] # 14 keys => 13 margins
    row1 = [F("Tab",1.5)] + [Key() for _ in range(12)] + [Key(width=1.5)]
    row2 = [F("Caps", 1.75)] + [Key() for _ in range(11)] + [F(RETURN, width=2.25+1*compensate)]
    row3 = [F(UP_WHITE_ARROW, 2.25)]+ [Key() for _ in range(10)] + [F(UP_WHITE_ARROW, width=2.75+2*compensate)]
    row4 = [F("Ctrl",1.5), F(YIN_YANG, 1.5), F("Alt", 1.5), Key(width=6.+7*compensate), F("Alt", 1.5), F(YIN_YANG, 1.5), F("Ctrl",1.5)]
    return [row0,row1,row2,row3,row4]

def html(u):
    if u==' ':
        return NBSP
    else:
        return '&#x%04x;' % ord(u)

def presentation(char,
                 ADD_BASE="<span>%s</span>%s"):    
    u = unicode(char) # just make sure
    if u in VISIBLE_FORMATTING:
        value = VISIBLE_FORMATTING[u]
    elif u in SHIN_DOTS:
        value = ADD_BASE % (HTML_SHIN, html(u))
    elif u in HATAFIM:
        value = ADD_BASE % (HTML_ALEPH, html(u))
    elif u==HOLAM_HASER_FOR_VAV:
        value = ADD_BASE % (HTML_VAV, html(u))
    elif category(u)==NONSPACING_MARK:
        value = ADD_BASE % (HTML_MEM, html(u))
    else:
        value = html(u)
        
    value = StyleStr(value)
    if u in VISIBLE_FORMATTING:
        value.style = "kbsymbols"
    elif category(u)==NONSPACING_MARK:
        value.style = "kbdecoration"
    value.hexa = "%04X" % ord(u)
    value.name = char_name(u)
    value.char = u
    return value
 


def make_view_keys(name):
    qs = KeyBinding.objects.filter(level__layout__name=name).select_related("level")
    keys = list(qs)
    if not keys:
        raise Http404("Nothing defined for layout: " + name)
    layout = keys[0].level.layout
    kb = kb105()
    for k in keys:
        kb[k.row][k.pos][k.mod_level] = presentation(k.char)
    
    ref1 = layout.ref1
    if ref1:
        for k in ref1.keybinding_set.all():
            kb[k.row][k.pos].ref1 = k.char
    
    ref2 = layout.ref2
    if ref2:
        for k in ref2.keybinding_set.all():
            kb[k.row][k.pos].ref2 = k.char
    
    return layout, kb

def show_layout(request, name='si1452'):
    layout, kb = make_view_keys(name)
    font_form = FontForm({"font":layout.font})
    return render_to_response("keyboard.html", 
                              {'key_rows':kb, 'name':name, 
                               'font': layout.font, 'font_form':font_form,
                               'caps_choices': caps.choices(),
                               'static_root': settings.MEDIA_URL},
                              context_instance=RequestContext(request))

def gen_xkb(request, name):
    _, kb = make_view_keys(name)
    group_name = request.GET.get('group_name', name)
    mirrored = request.GET.get('mirrored', False)
    caps_func = caps.get(request.GET.get('caps_option', None))
    kb = [[k for k in row if isinstance(k, Key)] for row in kb]
    for row in kb:        
        for key in row:
            key.mirrored = mirrored
            key.caps_keys = caps_func(key)
            
    response = render_to_response("xkb_symbols", {
                                    'key_rows':kb, 
                                    'name':name,
                                    'group_name': group_name,
                                    'mirrored': mirrored,
                                    'mirror_comment': km.XKB_MIRROR_COMMENT if mirrored else "",
                                    'caps_defined': any(k.caps_keys for k in row for row in kb) 
                                  }, 
                                  context_instance=RequestContext(request),
                                  mimetype="text/plain")
    response['Content-Disposition'] = 'attachment; filename=%s' % name
    return response

def gen_klc(request, name):
    _, kb = make_view_keys(name)
    params = {}
    for n in ("localename","localeid","languagename"):
        params[n] = request.GET.get(n, None)
    mirrored = request.GET.get('mirrored', False)
    caps_func = caps.get(request.GET.get('caps_option', None))
    params['mirrored'] = mirrored
    for row,row_keys in enumerate(kb):        
        for pos,key in enumerate(row_keys):
            if not isinstance(key, Key):
                continue
            key.mirrored = mirrored
            key.caps_keys = caps_func(key)
            key.klc_annotate(row, pos)
    kb = [[k for k in r if isinstance(k, Key)] for r in kb]
    params.update(dict(name=name,
                       key_rows=kb,
                       mirrored=mirrored,
                       mirror_comment=km.KLC_MIRROR_COMMENT if mirrored else ""))
    save_charset = settings.FILE_CHARSET
    try:
        settings.FILE_CHARSET = 'utf-16'
        response = render_to_response("symbols.klc", params, 
                                      context_instance=RequestContext(request),
                                      mimetype="text/plain")
        response._charset = 'utf-16'
        response['Content-Disposition'] = 'attachment; filename=%s.klc' % name
        return response
    finally:
        settings.FILE_CHARSET = save_charset

def gen_map(request, name):
    type = request.GET.get('type', 'undefined')
    if type=='xkb':
        return gen_xkb(request, name)
    elif type=='klc':
        return gen_klc(request, name)
    else:
        raise Http404("Keymap of type '%s' not supported" % type)

   
def editable(char):
    if char:
        n = ord(char)
        return char if 32<n<=127 else ("%04X" % n) # note 32=space done by hexa
    else:
        return char
        
@transaction.commit_on_success
def edit_key(request, name=None, row=None, pos=None):
    if request.method=='GET':
        # Show the existing key bindings
        layout = get_object_or_404(Layout, name=name)
        font = layout.font
        row = int(row)
        pos = int(pos)
        levels_qs = KeyBinding.objects.filter(level__layout=layout, row=row, pos=pos)
        levels_all = levels_qs.select_related('level')[:]
        levels = [None]*5
        for k in levels_all:
            levels[k.mod_level]=k.char
        form_data = dict(layout=layout, row=row, pos=pos)
        field_names = ["level%d" % (i+1) for i in range(4)]
        form_data.update(dict(zip(field_names, map(editable, levels[1:]))))
        form = KeyForm(form_data)
        pres1, pres2, pres3, pres4 = [presentation(c) if c else None for c in levels[1:]]
        ref = get_object_or_404(KeyBinding, level=layout.ref1, row=row,pos=pos)
        ref = presentation(ref.char)
        
    elif request.method!='POST':
        return HttpResponseBadRequest()
    else:
        form = KeyForm(request.POST)
        if form.is_valid():
            row=form.cleaned_data['row']
            pos=form.cleaned_data['pos']
            layout=form.cleaned_data['layout']
            key_params = dict(level__layout=layout, row=row, pos=pos)
            def update_level(lvl):
                value = form.cleaned_data['level%d' % lvl]
                if value:
                    level,created = Level.objects.get_or_create(layout=layout, level=lvl)
                    binding,created = KeyBinding.objects. \
                                      get_or_create(defaults={'char': value, 'level':level},
                                                    level__level=lvl, **key_params)
                    if not created:
                        binding.char = value
                        binding.save()
                else:
                    KeyBinding.objects.filter(level__level=lvl, **key_params).delete()
            map(update_level,[1,2,3,4])
            return redirect(reverse('show-layout', kwargs={"name": form.cleaned_data['layout'].name}))
    
    return render_to_response("edit_key.html", locals(), context_instance=RequestContext(request) )

def clone_layout(request, name):
    if request.method!='POST':
        return HttpResponseBadRequest()
    form = CloneForm(request.POST)
    if form.is_valid():
        layout = get_object_or_404(Layout, name=name)
        new_name = form.cleaned_data['new_name']
        layout.clone(new_name)
        return redirect(reverse('show-layout', kwargs={"name": new_name}))
    else:
        return redirect(reverse('layouts'))
    
def set_layout_font(request, name):
    if request.method!='POST':
        return HttpResponseBadRequest()
    form = FontForm(request.POST)
    if form.is_valid():
        layout = get_object_or_404(Layout, name=name)
        layout.font = form.cleaned_data['font']
        layout.save()
        return redirect(reverse('show-layout', kwargs={"name": name}))
        
