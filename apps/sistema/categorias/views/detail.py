from django.views.generic import DetailView
from .base import CategoriaMixin


class CategoriaDetailView(CategoriaMixin, DetailView):
    permission_required = "inventario_categorias.view_categoria"
    template_name = "categorias/detail.html"
