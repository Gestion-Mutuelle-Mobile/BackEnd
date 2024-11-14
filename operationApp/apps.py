from django.apps import AppConfig


class OperationappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'operationApp'

# mutualApp/apps.py


class MutualAppConfig(AppConfig):
    name = 'mutualApp'

    def ready(self):
        # Importer les signaux pour enregistrer les écouteurs
        import operationApp.signals
