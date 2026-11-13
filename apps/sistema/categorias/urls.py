from django.urls import path
from .views.list import CategoriaListView
from .views.create import CategoriaCreateView
from .views.update import CategoriaUpdateView
from .views.detail import CategoriaDetailView
from .views.archive import CategoriaArchiveView

urlpatterns = [
    path("categorias/", CategoriaListView.as_view(), name="categorias-list"),
    path("categorias/crear/", CategoriaCreateView.as_view(), name="categorias-create"),
    path("categorias/<int:pk>/editar/", CategoriaUpdateView.as_view(), name="categorias-update"),
    path("categorias/<int:pk>/", CategoriaDetailView.as_view(), name="categorias-detail"),
    path("categorias/<int:pk>/archivar/", CategoriaArchiveView.as_view(), name="categorias-archive"),
]
# Alias de enlaces existentes: misma funcionalidad, sin una segunda app.
for prefix, list_url, action_url in [("inventario", "inventory/categories/list/", "inventory/"), ("catalogo", "catalog/categories/list/", "categories/")]:
    urlpatterns += [
        path(list_url, CategoriaListView.as_view(), name=f"categorias-{prefix}-list"),
        path(action_url+"add/", CategoriaCreateView.as_view(), name=f"categorias-{prefix}-add"),
        path(action_url+"update/<int:pk>/", CategoriaUpdateView.as_view(), name=f"categorias-{prefix}-update"),
        path(action_url+"detail/<int:pk>/", CategoriaDetailView.as_view(), name=f"categorias-{prefix}-detail"),
        path(action_url+"delete/<int:pk>/", CategoriaArchiveView.as_view(), name=f"categorias-{prefix}-delete"),
    ]
