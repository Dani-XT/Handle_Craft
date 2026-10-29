from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

def get_all_entidades():
    data_content = []
    contents = ContentType.objects.all().order_by('id')

    for content in contents:
        permisos = list(content.permission_set.all())
        
        data_permisos = []
        grupos_totales = set()

        for permiso in permisos:
            
            data_permisos.append({
                "id": permiso.id,
                "name": permiso.name,
            })
            
            for grupo in permiso.group_set.all():
                grupos_totales.add((grupo.id, grupo.name))
            
        data_grupos = [{"id": gid, "name": gname} for gid, gname in grupos_totales]
            
        data_content.append({
            "id": content.id,
            "model": content.model,
            "app_label": content.app_label,
            "permisos": data_permisos,
            "grupos": data_grupos
        })
    
    return data_content