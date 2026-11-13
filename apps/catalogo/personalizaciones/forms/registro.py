from django import forms
from ..models import Diseno


class DisenoForm(forms.ModelForm):
    class Meta:
        model = Diseno
        fields = ('cliente', 'nombre')
