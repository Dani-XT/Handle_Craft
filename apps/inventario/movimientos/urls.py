from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.inventario.movimientos.views.views import MovimientosListView

urlpatterns = [
    path(
        "movements/list/",
        login_required(MovimientosListView.as_view()),
        name = "movimientos-list"
    ),
]