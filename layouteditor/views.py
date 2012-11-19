import re
from unicodedata import category, name as char_name

from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.db import transaction
from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponseBadRequest, HttpResponse,\
    HttpResponseForbidden
from django.template import loader
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from models import KeyBinding, Layout, Level, KeyChange
from forms import KeyForm, CloneForm, LayoutDescriptionForm
import keymaps as km
import caps_options_utils as caps
import caps_options # just to load the options;  @UnusedImport


__all__ = ["show_layout", "clone_layout", "change_description",
           "edit_key", "undo_edit", "redo_edit",
           "gen_xkb", "gen_klc", "gen_map",
           "gen_xkb_patch",
           "search",
]
                               
class InconsistentUndo(SuspiciousOperation):
    pass

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
HTML_BET = u'&#x05d1;'
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
        if self.caps_keys: self.caps_keys = list(self.caps_keys)        
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
        value = ADD_BASE % (HTML_BET, html(u))
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
 


def make_view_keys(owner, name):
    qs = KeyBinding.objects.filter(level__layout__owner__username=owner,
                                   level__layout__name=name)
    qs = qs.select_related("level")
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

def make_one_key(layout, row, pos, bindings):
    ref1 = ref2 = None
    if layout.ref1:
        try: 
            ref1 =  layout.ref1.keybinding_set.get(row=row, pos=pos).char
        except KeyBinding.DoesNotExist:
            pass
        
    if layout.ref2:
        try: 
            ref2 =  layout.ref2.keybinding_set.get(row=row, pos=pos).char
        except KeyBinding.DoesNotExist:
            pass
    
    key = Key(ref1, ref2)
    for b in bindings:
        if b: key[b.mod_level] = presentation(b.char)
    return key 
    
def show_layout(request, owner, name):
    layout, kb = make_view_keys(owner, name)
    params = {'key_rows':kb, 'name':name, 'owner': owner,
              'caps_choices': caps.choices()
              } 
    user = request.user
    can_edit = params['can_edit'] = can_edit_for(user, owner)
    if user.is_authenticated():
        default_clone_name = get_default_clone_name(user, name)        
        clone_form = CloneForm(user, {'new_name':default_clone_name})
        params['clone_form'] = clone_form
    if can_edit:
        params['undo'] = KeyChange.objects.to_undo(layout)
        params['redo'] = KeyChange.objects.to_redo(layout)
        params['descr_form'] = LayoutDescriptionForm(layout)
    else:
        params['description'] = layout.description
    return render_to_response("keyboard.html", params, 
                              context_instance=RequestContext(request))

def gen_xkb(request, owner, name):
    layout, kb = make_view_keys(owner, name)
    group_name = request.GET.get('group_name', name)
    mirrored = request.GET.get('mirrored', False)
    caps_func = caps.get(request.GET.get('caps_option', None))
    caps_key_type = caps_func.key_type or request.GET.get('caps_key_type', caps.EIGHT_LEVEL)
    if caps_key_type not in caps.CAPS_KEY_TYPES:
        raise Http404("Unrecognized key type requested")
    kb = [[k for k in row if isinstance(k, Key)] for row in kb]
    for row in kb:        
        for key in row:
            key.mirrored = mirrored
            key.caps_keys = caps_func(key)
    
    user_profile = layout.owner_profile()
     
    response = render_to_response("xkb_symbols", {
                                    'key_rows':kb, 
                                    'name':name,
                                    'group_name': group_name,
                                    'mirrored': mirrored,
                                    'mirror_comment': km.XKB_MIRROR_COMMENT if mirrored else "",
                                    'caps_defined': any(k.caps_keys for k in row for row in kb),
                                    'caps_key_type': caps_key_type,
                                    'description' : layout.description,
                                    'author' : user_profile.name,
                                    'affiliation' : user_profile.affiliation,
                                    'copyright' : layout.copyright,
                                  }, 
                                  context_instance=RequestContext(request),
                                  mimetype="text/plain")
    response['Content-Disposition'] = 'attachment; filename=il_%s' % name
    return response

def gen_xkb_patch(request, owner, name):
    layout = get_object_or_404(Layout, owner__username=owner, name=name)
    desc_line = layout.description.splitlines()[0] if layout.description else ""
    response = render_to_response("xkb.patch", {
                                    'name': layout.name,
                                    'desc_line': desc_line,
                                  },
                                  context_instance=RequestContext(request),
                                  mimetype="text/plain")
    response['Content-Disposition'] = 'attachment; filename=xkb_%s.patch' % name
    return response

def gen_klc(request, owner, name):
    layout, kb = make_view_keys(owner, name)
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
    user_profile = layout.owner_profile()
    params.update({'description' : layout.description,
                   'author' : user_profile.name,
                   'affiliation' : user_profile.affiliation,
                   'copyright' : layout.copyright,
                   })
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

def gen_map(request, owner, name):
    file_type = request.GET.get('type', 'undefined')
    if file_type=='xkb':
        return gen_xkb(request, owner, name)
    elif file_type=='klc':
        return gen_klc(request, owner, name)
    else:
        raise Http404("Keymap of type '%s' not supported" % file_type)

   
def editable(char):
    if char:
        n = ord(char)
        return char if 32<n<=127 else ("%04X" % n) # note 32=space done by hexa
    else:
        return char
        
def get_all_levels(layout, row, pos):
    levels_qs = KeyBinding.objects.filter(level__layout=layout, row=row, pos=pos)
    levels_all = levels_qs.select_related('level')[:]
    levels = [None] * 5
    for k in levels_all:
        levels[k.mod_level] = k.char
    
    return levels

def render_json_response(accepted, template_name, dictionary, request):
    """
    Render a template into an HTML, and plant it as "content" in a json response
    together with an indication whether the request was accepted
    """
    html = loader.render_to_string(template_name, dictionary,
                                   context_instance=RequestContext(request))
    accepted = True if accepted else False # normalization
    contents = simplejson.dumps(dict(accepted=accepted, fragment=html))
    return HttpResponse(contents, mimetype="application/json")
    
@login_required
@transaction.commit_on_success
def edit_key(request, owner, name, row, pos):
    if not can_edit_for(request.user, owner):
        return HttpResponseForbidden()
    if request.method=='GET':
        # Show the existing key bindings
        layout = get_object_or_404(Layout, owner__username=owner, name=name)
        row = int(row)
        pos = int(pos)
        levels = get_all_levels(layout, row, pos)
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
            change = KeyChange(layout=layout, row=row, pos=pos)
            key_params = dict(level__layout=layout, row=row, pos=pos)
            def update_level(lvl):
                value = form.cleaned_data['level%d' % lvl]
                if value:
                    change.set_after(lvl, value)
                    level,created = Level.objects.get_or_create(layout=layout, level=lvl)
                    binding,created = KeyBinding.objects. \
                                      get_or_create(defaults={'char': value, 'level':level},
                                                    level__level=lvl, **key_params)
                    if not created:
                        change.set_before(lvl, binding.char)
                        binding.char = value
                        binding.save()
                    return binding
                else:
                    try: 
                        binding = KeyBinding.objects.get(level__level=lvl, **key_params)
                        change.set_before(lvl, binding.char)
                        binding.delete()
                    except KeyBinding.DoesNotExist:
                        # Nothing deleted, no change done
                        pass
                    return None
            bindings = map(update_level,[1,2,3,4])
            if change.before!=change.after:
                change.save()
                KeyChange.objects.clear_redo_stack(layout)
            if request.is_ajax():
                key = make_one_key(layout, row, pos, bindings)
                return render_json_response(True, "key_display.html", {'key':key}, request)
            else:
                return redirect(reverse('show-layout', kwargs={"name": layout.name, "owner": layout.owner}))

        # Post invalid form under AJAX
        if request.is_ajax():
            return render_json_response(False, "edit_key_fragment.html", locals(), request)
    
    # Get, or post-invalid and not AJAX
    print "Rendering form to response!"
    return render_to_response("edit_key_fragment.html", locals(), context_instance=RequestContext(request) )

@login_required
@transaction.commit_on_success()
def undo_redo_edit(request, owner, name, redo):
    if not can_edit_for(request.user, owner):
        return HttpResponseForbidden()
    if request.method!='POST':
        return HttpResponseBadRequest()
    
    layout = get_object_or_404(Layout, owner__username=owner, name=name)
    change = KeyChange.objects.to_undo(layout) if not redo else KeyChange.objects.to_redo(layout) 
    bindings = set()
    if change:
        cbefore, cafter = (change.before, change.after) if not redo else (change.after, change.before) 
        for level in layout.level_set.all():
            idx = level.level-1
            before,after = cbefore[idx], cafter[idx]
            params = dict(level=level, row=change.row, pos=change.pos)
            if before!=after:
                
                if before==KeyChange.NULL:
                    if KeyBinding.objects.filter(**params).count()!=1:
                        raise InconsistentUndo
                    KeyBinding.objects.filter(**params).delete()
                else:
                    binding,created = KeyBinding.objects.get_or_create(defaults={'char': before, 'level':level},
                                                                       **params)
                    if after != (KeyChange.NULL if created else binding.char):
                        raise InconsistentUndo                    
                    if not created:
                        binding.char = before
                        binding.save()
                    bindings.add(binding)
            else:
                bindings.add(KeyBinding(level=level, char=before))
        change.done = redo
        change.save()
        
        if request.is_ajax():
            key = make_one_key(layout, change.row, change.pos, bindings)
            return render_json_response(True, "key_display.html", {'key':key}, request)
        else:
            return redirect(reverse('show-layout', kwargs={"name": layout.name, "owner": layout.owner}))
    else:
        # TODO: Better handling?
        raise Http404()

def undo_edit(request, owner, name):
    return undo_redo_edit(request, owner, name, False)

def redo_edit(request, owner, name):
    return undo_redo_edit(request, owner, name, True)

@login_required
@transaction.commit_on_success()
def change_description(request, owner, name):    
    if not can_edit_for(request.user, owner):
        return HttpResponseForbidden()
    if request.method!='POST':
        return HttpResponseBadRequest()
    
    layout = get_object_or_404(Layout, owner__username=owner, name=name)
    form = LayoutDescriptionForm(layout, request.POST)
    if form.is_valid():
        form.save(commit=True)
    else:
        messages.add_message(request, messages.ERROR, "Unexpected error encountered. Description not changed")
    return redirect(reverse('show-layout', kwargs={"name": name, "owner": owner}))
            
def clone_layout(request, owner, name):
    user = request.user
    if not user.is_authenticated():
        messages.add_message(request, messages.ERROR, "You need to be logged in to create a layout")
        return redirect(reverse('show-layout', kwargs={"name": name, "owner": owner}))
    if request.method!='POST':
        return HttpResponseBadRequest()
    form = CloneForm(user, request.POST)
    if form.is_valid():
        layout = get_object_or_404(Layout, owner__username=owner, name=name)
        new_name = form.cleaned_data['new_name']
        layout.clone(user, new_name)
        return redirect(reverse('show-layout', kwargs={"name": new_name, "owner": user}))
    else:
        for e in form.non_field_errors():
            messages.add_message(request, messages.ERROR, e)
        return redirect(reverse('show-layout', kwargs={"name": name, "owner": owner}))
            
def can_edit_for(request_user, username):
    return request_user.is_authenticated and \
            (request_user.is_staff or request_user.username==username)

def get_default_clone_name(user, name):
    name_query = Layout.objects.filter(owner=user).values_list('name', flat=True)
    existing_names = frozenset(name_query)
    try:
        base, suff = name.rsplit("_",1)
        suffix = int(suff)
    except ValueError:
        suffix = 1
    else:
        name = base

    if name not in existing_names:
        return name
        
    while True:
        default = "%s_%d" % (name,suffix)
        if default not in existing_names:
            return default
        suffix += 1

def search(request):
    if request.method=='GET':
        search = request.GET.get("search",None)
        if not search:
            return redirect(reverse("home"))
        layouts = Layout.objects.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return render_to_response("layout_search.html", locals(), context_instance=RequestContext(request) ) 
