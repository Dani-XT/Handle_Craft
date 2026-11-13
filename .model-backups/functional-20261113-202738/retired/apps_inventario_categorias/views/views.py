from django.views.generic import TemplateView
from apps.inventario.categorias.models import Categoria
from django.contrib.auth.mixins import PermissionRequiredMixin

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

class CategoriaInventarioListView(PermissionRequiredMixin, TemplateView):
    permission_required = ("inventario_categorias.view_categoria")
    template_name = "categorias-inventario-list.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        context.update(
            {
                "categorias": Categoria.objects.internas()
            }
        )

        TemplateHelper.map_context(context)
        return context