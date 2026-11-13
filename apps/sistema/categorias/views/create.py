from django.views.generic import CreateView
from .base import CategoriaMixin


class CategoriaCreateView(CategoriaMixin, CreateView):
    permission_required = "inventario_categorias.add_categoria"
    template_name = "categorias/form.html"
