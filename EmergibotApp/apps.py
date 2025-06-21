from django.apps import AppConfig


class EmergibotappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'EmergibotApp'

    def ready(self):
        import EmergibotApp.signals
