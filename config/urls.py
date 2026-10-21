"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

from web_project.views import SystemView

urlpatterns = [
    path('', include("apps.home.urls")),
    path('', include("apps.orders.urls")),

    # ACCESO
    path('', include("apps.acceso.groups.urls")),
    path('', include("apps.acceso.permissions.urls")),
    path('', include("apps.acceso.technicians.urls")),

    # ACTAS
    path('', include("apps.actas.clients.urls")),
    path('', include("apps.actas.computers_forms.urls")),
    path('', include("apps.actas.locations.urls")),

    # ACTIVOS
    path('', include("apps.activos.categories.urls")),
    path('', include("apps.activos.computers.urls")),
    path('', include("apps.activos.movements.urls")),
    path('', include("apps.activos.supplies.urls")),
    path('', include("apps.activos.warehouse.urls")),

    # AUTOMATIZACION
    path('', include("apps.automation.automation.urls")),

    # COMPRAS
    path('', include("apps.compras.oc.urls")),
    path('', include("apps.compras.providers.urls")),

    # ETL
    path('', include("apps.ETL.etl.urls")),

    # QR
    path('', include("apps.QR.qr_soporte.urls")),

    # SISTEMA
    path('', include("apps.sistema.emails.urls")),
    path('', include("apps.sistema.sex.urls")),

    path('', include("apps.auth.urls")),

    path('admin/', admin.site.urls),
]

handler404 = SystemView.as_view(template_name="misc_error.html", status=404)
handler403 = SystemView.as_view(template_name="misc_not_authorized.html", status=403)
handler400 = SystemView.as_view(template_name="misc_error.html", status=400)
handler500 = SystemView.as_view(template_name="misc_error.html", status=500)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)