from django.views.generic import TemplateView

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from apps.acceso.permisos.helpers import get_all_entidades

class PermisosListView(TemplateView):
    template_name = "permisos-list.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update(
            {
                "entidades": get_all_entidades(),
                # "entidades_excepts": get_all_entidades_excluidas(),
            }
        )
        TemplateHelper.map_context(context)
        return context