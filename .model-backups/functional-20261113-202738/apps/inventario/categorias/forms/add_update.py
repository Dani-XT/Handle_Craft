from django import forms
from apps.inventario.categorias.models import Categoria


class CategoriaInventarioAddUpdateForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ("nombre", "slug", "descripcion", "imagen", "parent", "publicada", "orden")
