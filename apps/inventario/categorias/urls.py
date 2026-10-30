from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.inventario.categorias.views.views import CategoriasCatalogoListView

urlpatterns = [
    path(
        "inventory/category/list/",
        login_required(CategoriasCatalogoListView.as_view()),
        name = "categorias-inventario-list"
    ),
]