import os
import json

from pathlib import Path
from dotenv import load_dotenv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.actas.locations.models import Sede, Campus, Edificio, Direccion
from apps.sistema.sex.models import Sexo

class Command(BaseCommand):
    help = "Pobla la base de datos con los registros principales del sistema para no hacerlo de manera manual"

    def handle(self, *args, **options):

        # Sistema
        self.poblar_sexos() # Listo ✅
        self.poblar_grupos() # Listo ✅
        self.poblar_sedes() # Listo ✅
        self.poblar_campus() # Listo ✅
        self.poblar_edificios() # Listo ✅
        self.poblar_direcciones() # Listo ✅

    def load_json(self, filename):
        ruta = Path(settings.BASE_DIR) / "data" / filename
        with open(ruta, "r", encoding="utf-8") as f:
            raw = json.load(f)

        def clean_media_paths(obj):
            if isinstance(obj, str):
                if obj.startswith("/media/"):
                    return obj.replace("/media/", "")
                return obj
            
            if isinstance(obj, dict):
                return {k: clean_media_paths(v) for k, v in obj.items()}

            if isinstance(obj, list):
                return [clean_media_paths(item) for item in obj]

            return obj  # por si llegan ints, None, bool, etc.

        return clean_media_paths(raw)

    def poblar_sexos(self):
        data = self.load_json("sistema/sexos.json")["sexos"]
        for item in data:
            obj, creado = Sexo.objects.get_or_create(
                nombre = item["nombre"],
                defaults = {
                    "descripcion": item["descripcion"],
                    "avatar": item["avatar"],
                }
            )
            msg = f"Sexo '{obj.nombre}' {'creado' if creado else 'ya existe'}"
            self.stdout.write(self.style.SUCCESS(msg) if creado else self.style.WARNING(msg))

    def poblar_grupos(self):
        data = self.load_json("sistema/grupos.json")["grupos"]
        for item in data:
            obj, creado = Group.objects.get_or_create(
                name = item["name"],
                # defaults={
                #     "permisos"
                # }
            )
            msg = f"Grupo '{obj.name}' {'creada' if creado else 'ya existe'}"
            self.stdout.write(self.style.SUCCESS(msg) if creado else self.style.WARNING(msg))


    def poblar_sedes(self):
        data = self.load_json("direcciones/sedes.json")["sedes"]
        for item in data:
            obj, creado = Sede.objects.get_or_create(
                nombre = item["nombre"],
                defaults={
                    "descripcion": item["descripcion"],
                    "imagen": item["imagen"],
                })
            msg = f"Sede '{obj.nombre}' {'creada' if creado else 'ya existe'}"
            self.stdout.write(self.style.SUCCESS(msg) if creado else self.style.WARNING(msg))

    def poblar_campus(self):
        data = self.load_json("direcciones/campus.json")["campus"]
        for item in data:
            sede = Sede.objects.get(id=item["sede"])
            obj, creado = Campus.objects.get_or_create(
                nombre = item["nombre"],
                defaults = {
                    "sede": sede,
                    "imagen_light": item["imagen_light"],
                    "imagen_dark": item["imagen_dark"]
                }
            )
            msg = f"Campus '{obj.nombre}' {'creado' if creado else 'ya existe'}"
            self.stdout.write(self.style.SUCCESS(msg) if creado else self.style.WARNING(msg))

    def poblar_edificios(self):
        data = self.load_json("direcciones/edificios.json")["edificios"]
        for item in data:
            obj, creado = Edificio.objects.get_or_create(nombre = item["nombre"])
            msg = f"Edificio '{obj.nombre}' {'creado' if creado else 'ya existe'}"
            self.stdout.write(self.style.SUCCESS(msg) if creado else self.style.WARNING(msg))

    def poblar_direcciones(self):
        data = self.load_json("direcciones/direcciones.json")["direcciones"]
        for item in data:
            campus = Campus.objects.get(id=item["campus"])
            edificio = None
            if item["edificio"]:
                edificio = Edificio.objects.get(id=item["edificio"])
            
            obj, creado = Direccion.objects.get_or_create(
                direccion=item["direccion"],
                campus=campus,
                edificio=edificio
            )
            msg = f"Ubicación '{obj.direccion}' {'creada' if creado else 'ya existe'}"
            self.stdout.write(self.style.SUCCESS(msg) if creado else self.style.WARNING(msg))


# import json
# from collections import Counter
# from pathlib import Path

# from django.conf import settings
# from django.contrib.auth.models import Group, Permission
# from django.core.management.base import BaseCommand, CommandError
# from django.db import transaction

# from apps.core.models import Sexo
# from apps.locations.models import Campus, Direccion, Edificio, Sede


# class Command(BaseCommand):
#     help = (
#         "Carga y sincroniza los datos iniciales del sistema "
#         "desde los archivos JSON de la carpeta data."
#     )

#     requires_migrations_checks = True

#     def add_arguments(self, parser):
#         parser.add_argument("--dry-run", action="store_true", help="Valida y procesa los datos, pero revierte los cambios.",)

#     @transaction.atomic
#     def handle(self, *args, **options):
#         self.data_directory = Path(settings.BASE_DIR) / "data"
#         self.stats = Counter()
#         self.verbosity = options["verbosity"]

#         self.stdout.write(
#             self.style.MIGRATE_HEADING("Inicializando sistema...")
#         )

#         try:
#             self.load_sexos()
#             self.load_groups()

#             # El orden respeta las dependencias entre modelos.
#             sedes = self.load_sedes()
#             campus = self.load_campus(sedes)
#             edificios = self.load_edificios()
#             self.load_direcciones(campus, edificios)

#         except CommandError:
#             raise
#         except Exception as error:
#             raise CommandError(
#                 f"Error inesperado inicializando el sistema: {error}"
#             ) from error

#         if options["dry_run"]:
#             transaction.set_rollback(True)
#             self.stdout.write(
#                 self.style.WARNING(
#                     "Ejecución de prueba finalizada. "
#                     "No se guardaron cambios."
#                 )
#             )
#         else:
#             self.stdout.write(
#                 self.style.SUCCESS(
#                     "Sistema inicializado correctamente."
#                 )
#             )

#         self.print_summary()

#     # ------------------------------------------------------------------
#     # Lectura y validación de archivos
#     # ------------------------------------------------------------------

#     def load_json_list(
#         self,
#         relative_path,
#         root_key,
#         required_fields,
#     ):
#         path = self.data_directory / relative_path

#         if not path.exists():
#             raise CommandError(
#                 f"No se encontró el archivo: {path}"
#             )

#         if not path.is_file():
#             raise CommandError(
#                 f"La ruta no corresponde a un archivo: {path}"
#             )

#         try:
#             # utf-8-sig también acepta archivos UTF-8 con BOM.
#             content = path.read_text(encoding="utf-8-sig")
#             raw_data = json.loads(content)
#         except UnicodeDecodeError as error:
#             raise CommandError(
#                 f"El archivo {relative_path} no está codificado en UTF-8."
#             ) from error
#         except json.JSONDecodeError as error:
#             raise CommandError(
#                 f"JSON inválido en {relative_path}, "
#                 f"línea {error.lineno}, columna {error.colno}: "
#                 f"{error.msg}"
#             ) from error

#         if not isinstance(raw_data, dict):
#             raise CommandError(
#                 f"El contenido principal de {relative_path} "
#                 "debe ser un objeto JSON."
#             )

#         if root_key not in raw_data:
#             raise CommandError(
#                 f"El archivo {relative_path} no contiene "
#                 f"la propiedad '{root_key}'."
#             )

#         items = raw_data[root_key]

#         if not isinstance(items, list):
#             raise CommandError(
#                 f"La propiedad '{root_key}' de {relative_path} "
#                 "debe ser una lista."
#             )

#         identifiers = set()

#         for position, item in enumerate(items, start=1):
#             if not isinstance(item, dict):
#                 raise CommandError(
#                     f"El elemento {position} de {relative_path} "
#                     "debe ser un objeto."
#                 )

#             missing_fields = [
#                 field
#                 for field in required_fields
#                 if field not in item
#             ]

#             if missing_fields:
#                 raise CommandError(
#                     f"Elemento {position} de {relative_path}: "
#                     f"faltan los campos {', '.join(missing_fields)}."
#                 )

#             if "id" in item:
#                 source_id = str(item["id"])

#                 if source_id in identifiers:
#                     raise CommandError(
#                         f"ID externo duplicado '{source_id}' "
#                         f"en {relative_path}."
#                     )

#                 identifiers.add(source_id)

#         return items

#     # ------------------------------------------------------------------
#     # Funciones comunes
#     # ------------------------------------------------------------------

#     def upsert(self, model, *, lookup, defaults=None):
#         """
#         Crea un registro o sincroniza los campos presentes en defaults.

#         Retorna:
#             tuple[Model, str]: objeto y estado:
#             created, updated o unchanged.
#         """
#         defaults = defaults or {}

#         instance, created = model.objects.get_or_create(
#             **lookup,
#             defaults=defaults,
#         )

#         if created:
#             self.stats["created"] += 1
#             return instance, "created"

#         changed_fields = []

#         for field_name, expected_value in defaults.items():
#             current_value = getattr(instance, field_name)

#             # Los ImageField retornan un FieldFile.
#             if hasattr(current_value, "name"):
#                 current_value = current_value.name

#             if hasattr(expected_value, "name"):
#                 comparable_expected = expected_value.name
#             else:
#                 comparable_expected = expected_value

#             if current_value != comparable_expected:
#                 setattr(instance, field_name, expected_value)
#                 changed_fields.append(field_name)

#         if changed_fields:
#             instance.save(update_fields=changed_fields)
#             self.stats["updated"] += 1
#             return instance, "updated"

#         self.stats["unchanged"] += 1
#         return instance, "unchanged"

#     def get_reference(
#         self,
#         mapping,
#         source_id,
#         *,
#         model_name,
#         source_file,
#         allow_none=False,
#     ):
#         if source_id is None:
#             if allow_none:
#                 return None

#             raise CommandError(
#                 f"{source_file}: la referencia a {model_name} "
#                 "no puede ser null."
#             )

#         source_id = str(source_id)

#         try:
#             return mapping[source_id]
#         except KeyError as error:
#             raise CommandError(
#                 f"{source_file}: no existe {model_name} "
#                 f"con ID externo '{source_id}'."
#             ) from error

#     def report(self, model_name, instance, status):
#         if self.verbosity < 2:
#             return

#         styles = {
#             "created": self.style.SUCCESS,
#             "updated": self.style.WARNING,
#             "unchanged": self.style.NOTICE,
#         }

#         labels = {
#             "created": "creado",
#             "updated": "actualizado",
#             "unchanged": "sin cambios",
#         }

#         style = styles[status]
#         label = labels[status]

#         self.stdout.write(
#             style(f"{model_name}: {instance} ({label})")
#         )

#     # ------------------------------------------------------------------
#     # Datos del sistema
#     # ------------------------------------------------------------------

#     def load_sexos(self):
#         items = self.load_json_list(
#             "sistema/sexos.json",
#             "sexos",
#             required_fields=(
#                 "id",
#                 "nombre",
#                 "descripcion",
#                 "avatar",
#             ),
#         )

#         for item in items:
#             sexo, status = self.upsert(
#                 Sexo,
#                 lookup={
#                     "nombre": item["nombre"].strip(),
#                 },
#                 defaults={
#                     "descripcion": item["descripcion"].strip(),
#                     "avatar": item["avatar"],
#                 },
#             )

#             self.report("Sexo", sexo, status)

#     def load_groups(self):
#         items = self.load_json_list(
#             "sistema/grupos.json",
#             "grupos",
#             required_fields=(
#                 "nombre",
#                 "permisos",
#             ),
#         )

#         for item in items:
#             group_name = item["nombre"].strip()
#             permission_codes = item["permisos"]

#             if not isinstance(permission_codes, list):
#                 raise CommandError(
#                     f"Grupo '{group_name}': permisos debe ser una lista."
#                 )

#             group, created = Group.objects.get_or_create(
#                 name=group_name
#             )

#             if created:
#                 self.stats["created"] += 1
#                 status = "created"
#             else:
#                 self.stats["unchanged"] += 1
#                 status = "unchanged"

#             permissions = []

#             for permission_code in permission_codes:
#                 permission = self.get_permission(
#                     permission_code,
#                     group_name=group_name,
#                 )
#                 permissions.append(permission)

#             current_permission_ids = set(
#                 group.permissions.values_list("pk", flat=True)
#             )
#             new_permission_ids = {
#                 permission.pk
#                 for permission in permissions
#             }

#             if current_permission_ids != new_permission_ids:
#                 group.permissions.set(permissions)

#                 if status == "unchanged":
#                     self.stats["unchanged"] -= 1
#                     self.stats["updated"] += 1

#                 status = "updated"

#             self.report("Grupo", group, status)

#     def get_permission(self, permission_code, *, group_name):
#         if not isinstance(permission_code, str):
#             raise CommandError(
#                 f"Grupo '{group_name}': cada permiso debe ser texto."
#             )

#         try:
#             app_label, codename = permission_code.split(".", 1)
#         except ValueError as error:
#             raise CommandError(
#                 f"Grupo '{group_name}': el permiso "
#                 f"'{permission_code}' debe usar el formato "
#                 "'app_label.codename'."
#             ) from error

#         try:
#             return Permission.objects.get(
#                 content_type__app_label=app_label,
#                 codename=codename,
#             )
#         except Permission.DoesNotExist as error:
#             raise CommandError(
#                 f"Grupo '{group_name}': no existe el permiso "
#                 f"'{permission_code}'. ¿Ejecutaste migrate?"
#             ) from error
#         except Permission.MultipleObjectsReturned as error:
#             raise CommandError(
#                 f"Grupo '{group_name}': el permiso "
#                 f"'{permission_code}' no es único."
#             ) from error

#     # ------------------------------------------------------------------
#     # Ubicaciones
#     # ------------------------------------------------------------------

#     def load_sedes(self):
#         items = self.load_json_list(
#             "direccion/sedes.json",
#             "sedes",
#             required_fields=(
#                 "id",
#                 "nombre",
#             ),
#         )

#         mapping = {}

#         for item in items:
#             defaults = {}

#             # Solo sincroniza campos presentes en el JSON.
#             if "descripcion" in item:
#                 defaults["descripcion"] = item["descripcion"].strip()

#             if "imagen" in item:
#                 defaults["imagen"] = item["imagen"]

#             sede, status = self.upsert(
#                 Sede,
#                 lookup={
#                     "nombre": item["nombre"].strip(),
#                 },
#                 defaults=defaults,
#             )

#             mapping[str(item["id"])] = sede
#             self.report("Sede", sede, status)

#         return mapping

#     def load_campus(self, sedes):
#         items = self.load_json_list(
#             "direccion/campus.json",
#             "campus",
#             required_fields=(
#                 "id",
#                 "sede",
#                 "nombre",
#             ),
#         )

#         mapping = {}

#         for item in items:
#             sede = self.get_reference(
#                 sedes,
#                 item["sede"],
#                 model_name="Sede",
#                 source_file="direccion/campus.json",
#             )

#             defaults = {}

#             if "imagen_light" in item:
#                 defaults["imagen_light"] = item["imagen_light"]

#             if "imagen_dark" in item:
#                 defaults["imagen_dark"] = item["imagen_dark"]

#             if "descripcion" in item:
#                 defaults["descripcion"] = item["descripcion"].strip()

#             campus, status = self.upsert(
#                 Campus,
#                 lookup={
#                     "sede": sede,
#                     "nombre": item["nombre"].strip(),
#                 },
#                 defaults=defaults,
#             )

#             mapping[str(item["id"])] = campus
#             self.report("Campus", campus, status)

#         return mapping

#     def load_edificios(self):
#         items = self.load_json_list(
#             "direccion/edificios.json",
#             "edificios",
#             required_fields=(
#                 "id",
#                 "nombre",
#             ),
#         )

#         mapping = {}

#         for item in items:
#             edificio, status = self.upsert(
#                 Edificio,
#                 lookup={
#                     "nombre": item["nombre"].strip(),
#                 },
#             )

#             mapping[str(item["id"])] = edificio
#             self.report("Edificio", edificio, status)

#         return mapping

#     def load_direcciones(self, campus, edificios):
#         items = self.load_json_list(
#             "direccion/ubicaciones.json",
#             "ubicaciones",
#             required_fields=(
#                 "id",
#                 "campus",
#                 "edificio",
#                 "direccion",
#             ),
#         )

#         for item in items:
#             campus_instance = self.get_reference(
#                 campus,
#                 item["campus"],
#                 model_name="Campus",
#                 source_file="direccion/ubicaciones.json",
#             )

#             edificio = self.get_reference(
#                 edificios,
#                 item["edificio"],
#                 model_name="Edificio",
#                 source_file="direccion/ubicaciones.json",
#                 allow_none=True,
#             )

#             direccion, status = self.upsert(
#                 Direccion,
#                 lookup={
#                     "campus": campus_instance,
#                     "edificio": edificio,
#                     "direccion": item["direccion"].strip(),
#                 },
#             )

#             self.report("Dirección", direccion, status)

#     # ------------------------------------------------------------------
#     # Resumen
#     # ------------------------------------------------------------------

#     def print_summary(self):
#         self.stdout.write("")
#         self.stdout.write(
#             self.style.MIGRATE_HEADING("Resumen")
#         )
#         self.stdout.write(
#             f"  Creados:       {self.stats['created']}"
#         )
#         self.stdout.write(
#             f"  Actualizados:  {self.stats['updated']}"
#         )
#         self.stdout.write(
#             f"  Sin cambios:   {self.stats['unchanged']}"
#         )