from django.shortcuts import get_object_or_404


from django.contrib.contenttypes.models import ContentType






# --- | Permisos | ---
def get_all_permisos():
    return ContentType.objects.prefetch_related("permission_set").all()

def get_all_content_by_group(grupo):
    return ContentType.objects.filter(permission__group=grupo).distinct()
     


