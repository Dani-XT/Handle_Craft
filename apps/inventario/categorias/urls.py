from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.inventario.categorias.views.views import CategoriaInventarioListView


urlpatterns = [
    path(
        "inventory/categories/list/",
        login_required(CategoriaInventarioListView.as_view()),
        name = "categorias-inventario-list"
    ),
    path(
        "inventory/add/",
        login_required(CategoriaInventarioListView.as_view()),
        name = "categorias-inventario-add"
    ),
    path(
        "inventory/update/<int:pk>/",
        login_required(CategoriaInventarioListView.as_view()),
        name = "categorias-inventario-update"
    ),
    path(
        "inventory/detail/<int:pk>/",
        login_required(CategoriaInventarioListView.as_view()),
        name = "categorias-inventario-detail"
    ),
    path(
        "inventory/delete/<int:pk>/",
        login_required(CategoriaInventarioListView.as_view()),
        name = "categorias-inventario-delete"
    ),
]