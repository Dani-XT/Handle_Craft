from datetime import date
from django.db import migrations


def importar_precios(apps, schema_editor):
    Variante = apps.get_model("productos", "VarianteProducto")
    Lista = apps.get_model("precios", "ListaPrecio")
    Precio = apps.get_model("precios", "PrecioArticulo")
    db = schema_editor.connection.alias
    variantes = Variante.objects.using(db).all()
    if not variantes.exists():
        return
    lista = Lista.objects.using(db).create(codigo="PUBLICA-INICIAL", nombre="Precios públicos migrados", moneda="CLP", publica=True, activa=True)
    for variante in variantes.iterator():
        Precio.objects.using(db).create(lista=lista, articulo_id=variante.articulo_id, cantidad_desde=1, precio_unitario=variante.precio_base, vigente_desde=date(2000, 1, 1))


class Migration(migrations.Migration):
    dependencies = [("precios", "0001_initial"), ("productos", "0001_initial")]
    operations = [migrations.RunPython(importar_precios, migrations.RunPython.noop)]
