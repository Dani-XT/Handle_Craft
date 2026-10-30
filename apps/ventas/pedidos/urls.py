from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.ventas.pedidos.views.views import PedidosListView


urlpatterns = [
    path(
        "orders/list/",
        login_required(PedidosListView.as_view()),
        name = "pedidos-list"
    ),
]