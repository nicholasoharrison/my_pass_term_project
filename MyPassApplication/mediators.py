from .observer_registry import ObserverRegistry

class UIMediator:
    def __init__(self):
        self.components = {}

    def register(self, name, component):
        """Register a component with the mediator."""
        self.components[name] = component

    def notify(self, sender, event, data=None):
        """Handle communication between components."""
        if sender in self.components:
            print(f"Mediator: Received event '{event}' from '{sender}' with data {data}")
        
        # Notify registered components of relevant updates
        if event in ("password_created", "password_deleted"):
            if "SavedPasswords" in self.components:
                self.components["SavedPasswords"].update(event, data)
            if "Dashboard" in self.components:
                self.components["Dashboard"].update(event, data)


