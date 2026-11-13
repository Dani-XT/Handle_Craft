from django.views.generic import ListView
from .base import CategoriaMixin


class CategoriaListView(CategoriaMixin, ListView):
    permission_required = "inventario_categorias.view_categoria"
    template_name = "categorias/list.html"
    context_object_name = "categorias"
    paginate_by = 30

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.GET.get("visibilidad") == "publica":
            qs = qs.filter(publicada=True)
        return qs
