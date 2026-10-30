from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.catalogo.categorias.views.views import CategoriasCatalogoListView


urlpatterns = [
    path(
        "categories/list/",
        login_required(CategoriasCatalogoListView.as_view()),
        name = "categorias-catalogo-list"
    ),
    path(
        "categories/add/",
        login_required(CategoriasCatalogoListView.as_view()),
        name = "categorias-add"
    ),
    path(
        "categories/update/<int:pk>/",
        login_required(CategoriasCatalogoListView.as_view()),
        name = "categorias-update"
    ),
    path(
        "categories/detail/<int:pk>/",
        login_required(CategoriasCatalogoListView.as_view()),
        name = "categorias-detail"
    ),
    path(
        "categories/delete/<int:pk>/",
        login_required(CategoriasCatalogoListView.as_view()),
        name = "categorias-delete"
    ),
]