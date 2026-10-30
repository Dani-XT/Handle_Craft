from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.ventas.ventas.views.views import VentasListView

urlpatterns = [
    path(
        "ventas/list/",
        login_required(VentasListView.as_view()),
        name = "ventas-list"
    ),
]