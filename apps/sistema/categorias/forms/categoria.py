from django import forms
from apps.sistema.categorias.models import Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ("nombre", "slug", "descripcion", "imagen", "parent", "publicada", "orden")
