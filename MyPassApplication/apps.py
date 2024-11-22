from django.apps import AppConfig
from .mediators import UIMediator
from .components import SavedPasswordsComponent

class MypassapplicationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'MyPassApplication'

# Initialize Mediator and Components
mediator = UIMediator()
saved_passwords_component = SavedPasswordsComponent(mediator)