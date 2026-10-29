from django.views.generic import TemplateView

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from apps.sistema.sexo.models import Sexo

class SexoListView(TemplateView):
    template_name = "sex-list.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update(
            {
                "generos": Sexo.objects.all().order_by("id")
            }
        )
        TemplateHelper.map_context(context)
        return context