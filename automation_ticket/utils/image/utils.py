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

def image_rename():
    pass

