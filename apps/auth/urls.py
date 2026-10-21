from django.urls import path
from django.shortcuts import redirect

from django.contrib.auth.views import LogoutView

from apps.auth.views.login import LoginView
from apps.auth.views.register import RegisterView
from apps.auth.views.verify_email import VerifyEmailView, VerifyEmailTokenView, SendVerificationView
from apps.auth.views.forgot_password import ForgetPasswordView
from apps.auth.views.reset_password import ResetPasswordView

urlpatterns = [
    path("", lambda request: redirect('login')),

    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),

    path(
        "register/",
        RegisterView.as_view(template_name="register.html"),
        name="register"
    ),
    path(
        "verify_email/",
        VerifyEmailView.as_view(template_name="auth/verify_email.html"),
        name="verify-email-page",
    ),

    path(
        "verify/email/<str:token>/",
        VerifyEmailTokenView.as_view(),
        name="verify-email",
    ),

    path(
        "send_verification/",
        SendVerificationView.as_view(),
        name="send-verification",
    ),
    path(
        "forgot_password/",
        ForgetPasswordView.as_view(),
        name="forgot-password",
    ),

    path(
        "reset_password/<str:token>/",
        ResetPasswordView.as_view(template_name="reset_password.html"),
        name="reset-password",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name = "logout",
    ),
]