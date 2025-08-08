from django.apps import AppConfig

class MainConfig(AppConfig):  # Mude o nome da classe
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'  # Mude o nome da app