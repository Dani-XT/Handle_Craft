from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.actas.computers_forms.views.views import ComputersFormsListView

urlpatterns = [
    path(
        "computers-forms/list/",
        login_required(ComputersFormsListView.as_view()),
        name = "computers-forms-list",
    ),
]