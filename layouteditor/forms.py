from django import forms
from django.forms.widgets import HiddenInput
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from models import Layout

class UnicodeField(forms.CharField):
    def __init__(self, blank=True, *args, **kwargs):
        super(UnicodeField, self).__init__(min_length=1, max_length=4, *args, **kwargs)
        
    def to_python(self, value):
        if not value:
            return None
        if len(value)<=1:
            return super(UnicodeField, self).to_python(value)
        # else:
        try:
            hexa = int(str(value), 16)
            return unichr(hexa)
        except (TypeError, ValueError):
            raise ValidationError(self.error_messages['invalid'])

class KeyForm(forms.Form):
    layout = forms.ModelChoiceField(Layout.objects.all(), widget=HiddenInput)
    row = forms.IntegerField(min_value=0, max_value=4, widget=HiddenInput)
    pos = forms.IntegerField(min_value=0, max_value=15, widget=HiddenInput)
    level1 = UnicodeField()
    level2 = UnicodeField()
    level3 = UnicodeField(blank=True, required=False)
    level4 = UnicodeField(blank=True, required=False)
    
alphanumeric = RegexValidator(r'^\w+$')

class CloneForm(forms.Form):
    new_name = forms.CharField(max_length=64, validators=[alphanumeric])
    
class FontForm(forms.Form):
    font = forms.CharField(max_length=80, required=False)
