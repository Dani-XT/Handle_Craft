from django.urls import path
from django.shortcuts import redirect

from apps.landing.views.views import LandingView

urlpatterns = [
    path("", lambda request: redirect('landing')),


    path(
        "landing/",
        LandingView.as_view(template_name="landing.html"),
        name="landing",
    ),
]