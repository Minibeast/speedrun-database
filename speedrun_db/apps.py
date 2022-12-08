from django.apps import AppConfig

class SpeedrunDbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'speedrun_db'

    def ready(self):
        from . import signals
