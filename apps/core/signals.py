from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Modelos
from django.contrib.auth.models import Permission

@receiver(post_migrate)
def crear_descripcion_automatica(sender, app_config, **kwargs):
    for permiso in Permission.objects.filter(content_type__app_label=app_config.label):
        
        if permiso.name.lower().startswith("can add") or \
           permiso.name.lower().startswith("can change") or \
           permiso.name.lower().startswith("can delete") or \
           permiso.name.lower().startswith("can view"):

            accion = permiso.codename.split("_")[0].capitalize()
            permiso.name = accion
            permiso.save()