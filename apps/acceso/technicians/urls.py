from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.acceso.technicians.views.views import TechniciansListView
from apps.acceso.technicians.views.add_update import TechniciansAddUpdateView

from apps.acceso.technicians.views.status import TechnicianStatusView

urlpatterns = [
    path(
        "technicians/list/",
        login_required(TechniciansListView.as_view()),
        name = "technicians-list"
    ),
    path(
        "technicians/add/",
        login_required(TechniciansAddUpdateView.as_view()),
        name = "technicians-add"
    ),
    path(
        "technicians/update/<int:pk>/",
        login_required(TechniciansAddUpdateView.as_view()),
        name = "technicians-update",
    ),
    path(
        "technicians/<int:pk>/status/",
        login_required(TechnicianStatusView.as_view()),
        name="technicians-status",
    ),
]