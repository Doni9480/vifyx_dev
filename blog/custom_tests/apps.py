from django.apps import AppConfig


class CustomTestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'custom_tests'

    def ready(self):
        import custom_tests.signals
