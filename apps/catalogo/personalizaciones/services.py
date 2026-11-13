from django.core.exceptions import ValidationError
from django.db import transaction
from .models import PersonalizacionDetalle, AprobacionDiseno


@transaction.atomic
def aprobar_diseno(personalizacion_id, actor, comentario=""):
    detalle = PersonalizacionDetalle.objects.select_for_update().get(pk=personalizacion_id)
    cliente = detalle.version.diseno.cliente
    if not actor or not actor.is_authenticated or not (actor.is_staff or cliente.usuario_id == actor.pk):
        raise ValidationError("El cliente propietario o personal autorizado debe registrar la aprobación.")
    if detalle.is_archived or detalle.version.diseno.is_archived:
        raise ValidationError("La personalización debe estar activa.")
    detalle.full_clean()
    aprobacion, _ = AprobacionDiseno.objects.get_or_create(personalizacion=detalle, defaults={"comentario": comentario, "created_by": actor, "updated_by": actor})
    return aprobacion
