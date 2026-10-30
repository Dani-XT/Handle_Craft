from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.compras.proveedores.views.views import ProveedoresListView

urlpatterns = [
    path(
        "providers/list/",
        login_required(ProveedoresListView.as_view()),
        name = "proveedores-list"
    ),
    
]