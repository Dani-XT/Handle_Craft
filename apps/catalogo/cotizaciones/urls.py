from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.catalogo.cotizaciones.views.views import CotizacionesListView

urlpatterns = [
    path(
        "quotes/list/",
        login_required(CotizacionesListView.as_view()),
        name = "cotizaciones-list"
    ),
]