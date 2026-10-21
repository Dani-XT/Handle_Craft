from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.db import transaction
from django.core.exceptions import ValidationError

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

from apps.sistema.sex.models import Sexo
from apps.actas.locations.models import Campus, Direccion, Sede

# from automation_ticket.utils.validators.utils import rut_validator

User = get_user_model()

def grupos_asignables_por(actor):
    if not actor or not actor.is_authenticated:
        return Group.objects.none()

    grupos = Group.objects.prefetch_related(
        "permissions__content_type"
    ).order_by("name")

    if actor.is_superuser:
        return grupos

    permisos_actor = actor.get_all_permissions()
    grupos_permitidos = []

    for grupo in grupos:
        permisos_grupo = {
            f"{permiso.content_type.app_label}.{permiso.codename}"
            for permiso in grupo.permissions.all()
        }

        if permisos_grupo.issubset(permisos_actor):
            grupos_permitidos.append(grupo.pk)

    return Group.objects.filter(
        pk__in=grupos_permitidos
    ).order_by("name")

class TechniciansAddUpdateForm(forms.ModelForm):
    first_name = forms.CharField(label="Nombre", max_length=150)
    last_name = forms.CharField(label="Apellido", max_length=150)
    email = forms.EmailField(label="E-mail", )
    rut = forms.CharField(label="RUT", max_length=12)

    sexo = forms.ModelChoiceField(queryset=Sexo.objects.none(), required=True,)

    sede = forms.ModelChoiceField(queryset=Sede.objects.none())
    campus = forms.ModelChoiceField(queryset=Campus.objects.none())
    direccion = forms.ModelChoiceField(queryset=Direccion.objects.none())

    grupo = forms.ModelChoiceField(queryset=Group.objects.none(), required=False,)

    password1 = forms.CharField(label="Contraseña", required=False, strip=False,)
    password2 = forms.CharField(label="Confirmar contraseña", required=False, strip=False,)

    is_superuser = forms.BooleanField(required=False)

    admin_password = forms.CharField(label="Contraseña del administrador", required=False, strip=False, widget=forms.PasswordInput,)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "rut",
            "email",
            "sexo",
            "direccion",
        )

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.actor = actor

        self.fields["sexo"].queryset = (Sexo.objects.all().order_by("nombre"))

        self.fields["sede"].queryset = (Sede.objects.all().order_by("nombre"))
        self.fields["campus"].queryset = (Campus.objects.select_related("sede").order_by("nombre"))
        self.fields["direccion"].queryset = (Direccion.objects.select_related("edificio", "campus", "campus__sede",).order_by("direccion"))

        self.fields["grupo"].queryset = grupos_asignables_por(actor)

        self.original_is_superuser = bool(self.instance.pk and self.instance.is_superuser)

        if self.instance.pk:
            self.initial.setdefault(
                "is_superuser",
                self.instance.is_superuser,
            )

            grupo = self.instance.groups.first()

            if grupo:
                self.initial.setdefault("grupo", grupo.pk)

            if self.instance.direccion_id:
                direccion = self.instance.direccion

                self.initial.setdefault(
                    "direccion",
                    direccion.pk,
                )
                self.initial.setdefault(
                    "campus",
                    direccion.campus_id,
                )
                self.initial.setdefault(
                    "sede",
                    direccion.campus.sede_id,
                )

        

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        dominio = email.rpartition("@")[2]

        if dominio != "unab.cl":
            raise ValidationError(
                "Debes utilizar un correo institucional terminado en @unab.cl."
            )

        queryset = User.objects.filter(email__iexact=email)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError("Ya existe un usuario con este correo.")

        return email

    def clean_rut(self):
        rut = self.cleaned_data["rut"]
        queryset = User.objects.filter(rut__iexact=rut)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise ValidationError(
                "Ya existe un usuario con este RUT."
            )

    def clean(self):
        data = super().clean()

        password1 = data.get("password1")
        password2 = data.get("password2")
        sede = data.get("sede")
        campus = data.get("campus")
        direccion = data.get("direccion")
        grupo = data.get("grupo")
        is_superuser = data.get("is_superuser", False)
        admin_password = data.get("admin_password")

        creating = self.instance._state.adding

        if creating and not password1:
            self.add_error("password1", "Debes ingresar una contraseña.")

        if creating and not password2:
            self.add_error("password2", "Debes confirmar la contraseña.")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Las contraseñas no coinciden.")

        if password1 and password1 == password2:
            usuario_temporal = User(
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                email=data.get("email", ""),
            )

            try:
                password_validation.validate_password(
                    password1,
                    user=usuario_temporal,
                )
            except ValidationError as error:
                self.add_error("password1", error)

        # Validación jerárquica de ubicación.
        if sede and campus and campus.sede_id != sede.pk:
            self.add_error(
                "campus",
                "El campus seleccionado no pertenece a esta sede.",
            )

        if campus and direccion and direccion.campus_id != campus.pk:
            self.add_error(
                "direccion",
                "La dirección seleccionada no pertenece a este campus.",
            )

        promoting_to_superuser = (
            is_superuser
            and not self.original_is_superuser
        )

        if is_superuser:
            if not self.actor or not self.actor.is_superuser:
                self.add_error(
                    "is_superuser",
                    "No tienes autorización para asignar "
                    "privilegios de superadministrador.",
                )

            if grupo is not None:
                self.add_error(
                    "grupo",
                    "Un superadministrador no debe tener "
                    "un grupo asignado.",
                )

        if promoting_to_superuser:
            if not admin_password:
                self.add_error(
                    "admin_password",
                    "Debes confirmar tu contraseña.",
                )
            elif not self.actor.check_password(
                admin_password
            ):
                self.add_error(
                    "admin_password",
                    "La contraseña ingresada es incorrecta.",
                )

        elif not is_superuser and grupo is None:
            self.add_error(
                "grupo",
                "Debes seleccionar un grupo.",
            )

        self.actor.check_password(admin_password)

        return data

    @transaction.atomic
    def save(self):
        usuario = super().save(commit=False)

        crear_superusuario = self.cleaned_data["is_superuser"]

        usuario.email = self.cleaned_data["email"]
        usuario.is_superuser = crear_superusuario
        usuario.is_staff = crear_superusuario

        # ver que hace este bloque de codigo
        creating = self.instance._state.adding
        usuario = super().save(commit=False)

        if creating:
            usuario.is_active = True

        password = self.cleaned_data.get("password")

        if password:
            usuario.set_password(password)

        usuario.save()

        if crear_superusuario:
            usuario.groups.clear()
        else:
            usuario.groups.set([self.cleaned_data["grupo"]])

        if self.cleaned_data.get("password1"):
            usuario.set_password(self.cleaned_data["password1"])

        return usuario


    # def __init__(self, *args, tecnico = None, **kwargs):
    #     super().__init__(*args, **kwargs)

    #     self.tecnico = tecnico

    #     if self.tecnico is not None:
    #         self.initial.update(
    #             {
    #                 "nombre": tecnico.first_name,
    #                 "apellido": tecnico.last_name,
    #                 "email": tecnico.email,
    #                 "rut": tecnico.rut,
    #                 "sexo": tecnico.sexo.pk,
    #             }
    #         )

