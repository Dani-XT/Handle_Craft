import uuid
from datetime import timedelta, datetime

from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import get_user_model

from apps.auth.helpers import send_password_reset_email
from apps.auth.views import AuthView

Usuario = get_user_model()

class ForgetPasswordView(AuthView):
    template_name="forgot_password.html"
    
    def post(self, request):
        if request.method == "POST":
            email = request.POST.get("email")

            usuario = Usuario.objects.get(email=email)
            if not usuario:
                messages.error(request, "Email no existe.")
                return redirect("forgot-password")

            # Generate a token and send a password reset email here
            token = str(uuid.uuid4())

            # Set the token in the user's profile and add an expiration time (e.g., 24 hours from now)
            expiration_time = datetime.now() + timedelta(hours=24)

            
            usuario.forget_password_token = token
            usuario.forget_password_token_expiration = expiration_time
            usuario.save()

            # Send the password reset email
            send_password_reset_email(email, token)

            if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD:
                messages.success(request, "A password reset email has been sent. Please check your inbox")
            else:
                messages.error(request, "Email settings are not configured. Unable to send verification email.")


            return redirect("forgot-password")
