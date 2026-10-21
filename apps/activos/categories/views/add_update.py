from web_project import TemplateLayout
from django.views.generic import TemplateView
from web_project.template_helpers.theme import TemplateHelper

from django.contrib.auth.mixins import PermissionRequiredMixin

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from apps.activos.categories.models import Categoria




class CategoriasAddUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ("auth.view_user")
    template_name = "categorias/categorias_add_update.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        pk = self.kwargs.get('pk')
        categoria = get_object_or_404(Categoria, pk=pk) if pk else None

        context.update(
            {
                "categoria": categoria,
            }
        )
        TemplateHelper.map_context(context)
        return context
    
    def post(self, request, *args, **kwargs):
        pass