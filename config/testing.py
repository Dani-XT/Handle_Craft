"""Configuración exclusiva de pruebas; no usar al ejecutar el servidor."""
from .settings import *

SECRET_KEY = "test-only-handlekraft-integration-suite"
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
