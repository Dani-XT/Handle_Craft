from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.ventas.clientes.views.views import ClientesListView

urlpatterns = [
    path(
        "clients/list/",
        login_required(ClientesListView.as_view()),
        name = "clientes-list"
    ),
    
]