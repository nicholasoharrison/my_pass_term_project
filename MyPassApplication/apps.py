# apps.py
from django.apps import AppConfig
from .components import SavedPasswords, Dashboard
from .mediators import UIMediator
from .observer_registry import ObserverRegistry


class MypassapplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MyPassApplication'

    def ready(self):

        # Initialize mediator
        mediator = UIMediator()

        saved_passwords = SavedPasswords(mediator)
        dashboard = Dashboard(mediator)

        # Register components with the mediator
        mediator.register("SavedPasswords", saved_passwords)
        mediator.register("Dashboard", dashboard)

        # Register observers
        ObserverRegistry.register_observer("password_created", saved_passwords)
        ObserverRegistry.register_observer("password_created", dashboard)
        ObserverRegistry.register_observer("password_deleted", saved_passwords)
        ObserverRegistry.register_observer("password_deleted", dashboard)
