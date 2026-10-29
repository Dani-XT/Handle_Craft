from web_project import TemplateLayout
from django.views.generic import TemplateView
from web_project.template_helpers.theme import TemplateHelper

from django.contrib.auth.mixins import PermissionRequiredMixin

from django.shortcuts import redirect
from django.contrib import messages

# from apps.acceso.tecnicos.forms import GruposAddUpdateForm
# from apps.groups.helpers import get_grupo, get_all_permisos
from apps.acceso.grupos.helpers import get_all_permisos

class GruposAddUpdateView(PermissionRequiredMixin, TemplateView):
    permission_required = ("auth.add_group")
    template_name = "grupos-add-update.html"

    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        pk = self.kwargs.get('pk')
        # grupo = get_grupo(pk) if pk else None

        context.update(
            {
                # "grupo": grupo,
                "content_types": get_all_permisos()
            }
        )


        TemplateHelper.map_context(context)
        return context
    
    # def post(self, request, *args, **kwargs):
    #     pk = self.kwargs.get('pk')
    #     grupo = get_grupo(pk) if pk else None

    #     form = GruposAddUpdateForm(request.POST, instance=grupo)

    #     if form.is_valid():
    #         grupo = form.save()
    #         if pk:
    #             messages.success(request, f'Grupo {grupo.name} modificado correctamente')
    #         else:
    #             messages.success(request, f'Grupo {grupo.name} creado correctamente')
    #         return redirect("grupos-detail", grupo.pk)
    #     else:
    #         if pk:
    #             messages.error(request, f'Error al modificar {grupo.name}')
    #         else:
    #             messages.error(request, f'Error al crear usuario')

    #         context = self.get_context_data(form=form)
    #         return self.render_to_response(context)
     
    
    