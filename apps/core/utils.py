import os
import uuid

from django.utils.deconstruct import deconstructible
from django.core.exceptions import SuspiciousFileOperation

def image_exist(field):
    try:
        if not field or not getattr(field, "name", None):
            return False
        
        storage = getattr(field, "storage", None)
        if not storage:
            return False
        
        return storage.exists(field.name)

    except SuspiciousFileOperation:
        return False
    
    except Exception:
        return False

@deconstructible
class RenameImagen:
    def __init__(self, carpeta):
        self.carpeta = carpeta

    def __call__(self, instance, filename):
        extension = os.path.splitext(filename)[1].lower()
        codigo = uuid.uuid4().hex

        return f"{self.carpeta}/{codigo}{extension}"

