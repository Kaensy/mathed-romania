from django.apps import AppConfig


class PetsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pets"
    verbose_name = "Student Pets"

    def ready(self):
        from . import signals  # noqa: F401  -- registers post_save handler
