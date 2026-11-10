from django.urls import path

from django.contrib.auth.views import LogoutView

from apps.auth.views.login import LoginView
from apps.auth.views.register import RegisterView
from apps.auth.views.verify_email import VerifyEmailView, VerifyEmailTokenView, SendVerificationView
from apps.auth.views.forgot_password import ForgetPasswordView
from apps.auth.views.reset_password import ResetPasswordView

urlpatterns = [

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
        "verify-email/",
        VerifyEmailView.as_view(template_name="auth/verify_email.html"),
        name="verify-email-page",
    ),

    path(
        "verify/email/<str:token>/",
        VerifyEmailTokenView.as_view(),
        name="verify-email",
    ),

    path(
        "send-verification/",
        SendVerificationView.as_view(),
        name="send-verification",
    ),
    path(
        "forgot-password/",
        ForgetPasswordView.as_view(),
        name="forgot-password",
    ),

    path(
        "reset-password/<str:token>/",
        ResetPasswordView.as_view(template_name="reset_password.html"),
        name="reset-password",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name = "logout",
    ),
]