from django.contrib import messages
from django.urls import reverse_lazy
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect

from django.views.generic import FormView
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.core.exceptions import PermissionDenied

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from apps.activos.categories.forms.add_update import CategoriesAddUpdateForm

class CategoriesAddUpdateView(PermissionRequiredMixin, FormView):
    raise_exception = True
    template_name = "categories-add-update.html"
    form_class = CategoriesAddUpdateForm
    success_url = reverse_lazy("categories-list")
    permission_required = ("auth.add_group")


    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        # context.update(
        #     {
        #         "tecnico": self.get_object(),
        #     }
        # )
        TemplateHelper.map_context(context)
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)
        

# from web_project import TemplateLayout
# from django.views.generic import TemplateView
# from web_project.template_helpers.theme import TemplateHelper

# from django.contrib.auth.mixins import PermissionRequiredMixin

# from django.shortcuts import redirect, get_object_or_404
# from django.contrib import messages

# from apps.activos.categories.models import Categoria




# class CategoriasAddUpdateView(PermissionRequiredMixin, TemplateView):
#     permission_required = ("auth.view_user")
#     template_name = "categories-add-update.html"

#     def get_context_data(self, **kwargs):
#         context = TemplateLayout.init(self, super().get_context_data(**kwargs))
#         pk = self.kwargs.get('pk')
#         categoria = get_object_or_404(Categoria, pk=pk) if pk else None

#         context.update(
#             {
#                 "categoria": categoria,
#             }
#         )
#         TemplateHelper.map_context(context)
#         return context
    
#     def post(self, request, *args, **kwargs):
#         pass