from django.apps import AppConfig

app_name = 'users'

class UsersConfig(AppConfig):
    name = 'users'

    def ready(self):
        import users.signals

