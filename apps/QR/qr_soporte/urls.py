from django.urls import path
from django.contrib.auth.decorators import login_required

from apps.QR.qr_soporte.views.views import QrSoporteListView

urlpatterns = [
    path(
        "qr-soporte/list/",
        login_required(QrSoporteListView.as_view()),
        name = "qr-soporte-list",
    ),
]