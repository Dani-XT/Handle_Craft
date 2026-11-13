from django.views.generic import TemplateView
from django.contrib.auth.mixins import PermissionRequiredMixin

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from apps.catalogo.categorias.models import Categoria

class CategoriasCatalogoListView(PermissionRequiredMixin, TemplateView):
    permission_required = ("auth.view_user")
    template_name = "categorias-catalogo-list.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        context.update(
            {
                "categorias": Categoria.objects.all()
            }
        )

        TemplateHelper.map_context(context)
        return context