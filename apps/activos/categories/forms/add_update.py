from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError

from apps.activos.categories.models import Categoria

class CategoriesAddUpdateForm(forms.ModelForm):
    nombre = forms.CharField()
    descripcion = forms.Textarea()
    imagen = forms.ImageField()
    
    class Meta:
        model = Categoria
        fields = (
            "nombre",
            "descripcion",
            "imagen"
        )