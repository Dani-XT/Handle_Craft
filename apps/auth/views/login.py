from django.contrib import messages
from django.contrib.auth import login

from django.shortcuts import redirect

from django.utils.http import url_has_allowed_host_and_scheme

from apps.auth.forms.login import LoginForm
from apps.auth.views import AuthView

class LoginView(AuthView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form") or LoginForm()
        return context

    

    def post(self, request):
        form = LoginForm(request.POST)

        if form.is_valid():
            login(request, form.save())

            messages.success(request, "Sesion iniciada correctamente.")
            next_url = request.POST.get("next")

            if next_url and not url_has_allowed_host_and_scheme(next_url, {request.get_host()}, require_https=request.is_secure()):
                next_url = None

            return redirect(next_url or "home")

        messages.error(request, "No fue posible iniciar sesión. Revisa tus credenciales.")
        return self.render_to_response(self.get_context_data(form=form), status=400)
        