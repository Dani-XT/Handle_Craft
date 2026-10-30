from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.catalogo.productos.views.views import ProductosListView

urlpatterns = [
    path(
        "products/list/",
        login_required(ProductosListView.as_view()),
        name = "productos-list"
    ),
    
]