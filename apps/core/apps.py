from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'apps.core'
    label = 'core'

    def ready(self):
        import apps.core.signals
        from django.apps import apps
        from auditlog.registry import auditlog
        from apps.core.models import BaseModel
        for model in apps.get_models():
            if issubclass(model, BaseModel):
                auditlog.register(model, exclude_fields=["created_at", "updated_at"])
