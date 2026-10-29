from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.catalogo.productos.views.views import ProductosListView
from apps.catalogo.productos.views.add_update import ProductosAddUpdateView

urlpatterns = [
    path(
        "products/list/",
        login_required(ProductosListView.as_view()),
        name = "productos-list"
    ),
    path(
        "products/add/",
        login_required(ProductosAddUpdateView.as_view()),
        name = "productos-add"
    ),
    path(
        "products/update/<int:pk>/",
        login_required(ProductosAddUpdateView.as_view()),
        name = "productos-update"
    ),
    
]