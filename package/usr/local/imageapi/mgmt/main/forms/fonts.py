from django import forms

class FontMergerForm(forms.Form):
    font1 = forms.FileField(required=True)
    font2 = forms.FileField(required=True)
    
    
FONT_FORMAT_CHOICES = [
                       ("ttf", "TrueType (.ttf)"), 
                       ("otf", "OpenType (.otf)"), 
                       ("woff", "Web Open Font Format (.woff)")
                       ]

class FontConverterForm(forms.Form):
    font = forms.FileField(required=True)
    format = forms.ChoiceField(choices=FONT_FORMAT_CHOICES)

class FaviconGetterForm(forms.Form):
    url = forms.URLField(required=True, verify_exists=False)
