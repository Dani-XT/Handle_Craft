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
    # HOMES PRINCIPALES
    path('', include("apps.landing.urls")),    
    path('', include("apps.home.urls")),

    # ACCESO
    path('', include("apps.acceso.grupos.urls")),
    path('', include("apps.acceso.permisos.urls")),
    path('', include("apps.acceso.usuarios.urls")),

    # CATALOGO
    path('', include("apps.catalogo.categorias.urls")),
    path('', include("apps.catalogo.productos.urls")),

    # COMPRAS

    # INVENTARIO

    # PERSONAL (PERSONAS)

    # SISTEMA
    path('', include("apps.sistema.emails.urls")),
    path('', include("apps.sistema.sexo.urls")),

    # VENTAS

    # AUTENTICACION
    path('', include("apps.auth.urls")),

    path('admin/', admin.site.urls),
]

handler404 = SystemView.as_view(template_name="misc_error.html", status=404)
handler403 = SystemView.as_view(template_name="misc_not_authorized.html", status=403)
handler400 = SystemView.as_view(template_name="misc_error.html", status=400)
handler500 = SystemView.as_view(template_name="misc_error.html", status=500)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)