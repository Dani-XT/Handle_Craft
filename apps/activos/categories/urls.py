from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.activos.categories.views.views import CategoriesListView
from apps.activos.categories.views.add_update import CategoriesAddUpdateView

urlpatterns = [
    path(
        "categories/list/",
        login_required(CategoriesListView.as_view()),
        name = "categories-list",
    ),

    path(
        "categories/add/",
        login_required(CategoriesAddUpdateView.as_view()),
        name = "categories-add",
    ),
]