from django.db import migrations


def crear_unidades(apps, schema_editor):
    Unidad = apps.get_model("unidades", "UnidadMedida")
    for codigo, nombre, magnitud, decimales in [("un", "Unidad", "conteo", 0), ("kg", "Kilogramo", "masa", 3), ("m", "Metro", "longitud", 3), ("l", "Litro", "volumen", 3)]:
        Unidad.objects.using(schema_editor.connection.alias).get_or_create(codigo=codigo, defaults={"nombre": nombre, "simbolo": codigo, "magnitud": magnitud, "decimales": decimales})


class Migration(migrations.Migration):
    dependencies = [("unidades", "0001_initial")]
    operations = [migrations.RunPython(crear_unidades, migrations.RunPython.noop)]
