from django.views.generic import UpdateView
from .base import CategoriaMixin


class CategoriaUpdateView(CategoriaMixin, UpdateView):
    permission_required = "inventario_categorias.change_categoria"
    template_name = "categorias/form.html"
