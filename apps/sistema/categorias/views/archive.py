from django.views.generic import DetailView
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from django.contrib import messages
from .base import CategoriaMixin


class CategoriaArchiveView(CategoriaMixin, DetailView):
    permission_required = "inventario_categorias.change_categoria"
    template_name = "categorias/archive.html"

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.archive(request.user)
        except ValidationError as error:
            messages.error(request, str(error))
            return self.get(request, *args, **kwargs)
        return redirect(self.success_url)
