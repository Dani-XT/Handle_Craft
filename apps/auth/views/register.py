from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import login

from web_project.template_helpers.theme import TemplateHelper

from apps.auth.views import AuthView

from apps.auth.forms.register import RegisterUsuarioForm


class RegisterView(AuthView):
    template_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = kwargs.get("form") or RegisterUsuarioForm()
        
        context.update(
            {
                "form": form,
                # "regiones": Region.objects.all(),
                # "provincias": Provincia.objects.all(),
                # "comunas": Comuna.objects.all(),
                # "nivel_educacional": NivelEducacional.objects.all(),
                # "sexo": Usuario.Sexo.choices,
                # "situacion_previsional": SituacionPrevisional.objects.all(),
                # "condicion_habitacional": CondicionHabitacional.objects.all(),
                # "postulaciones_previas": PostulacionesPrevias.objects.all(),
            }
        )

        TemplateHelper.map_context(context)
        return context

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("home")
        
        return super().get(request)
    
    def post(self, request):
        form = UsuarioNaturalForm(request.POST)

        if form.is_valid():
            login(request, form.save())
            messages.success(request, "Usuario registrado con exito")
            return redirect('front:home')

        else:
            messages.error(request, "No se pudo completar el registro. Revisa los campos indicados.")
            return self.render_to_response(self.get_context_data(form=form))
