from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper
from apps.sistema.categorias.models import Categoria
from apps.sistema.categorias.forms.categoria import CategoriaForm


class CategoriaMixin(LoginRequiredMixin, PermissionRequiredMixin):
    model = Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy("categorias-list")
    context_object_name = "categoria"

    def get_queryset(self):
        return Categoria.objects.internas()

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        TemplateHelper.map_context(context)
        return context

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        return super().form_valid(form)
