from django.apps import AppConfig


class AposConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apos'

    def ready(self):
        import apos.signals
