from apps.core.forms import StyledModelForm
from apps.sistema.categorias.models import Categoria


class CategoriaForm(StyledModelForm):
    class Meta:
        model = Categoria
        fields = ("nombre", "slug", "descripcion", "imagen", "parent", "publicada", "orden")
