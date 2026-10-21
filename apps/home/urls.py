from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import HomeView

urlpatterns = [
    path(
        "home/",
        login_required(HomeView.as_view()),
        name = "home",
    ),
]