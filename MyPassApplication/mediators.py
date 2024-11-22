# mediators.py

# The UIMediator acts as a central hub for coordinating communication between various components like CreatePassword and SavedPasswords.
class UIMediator:
    def __init__(self):
        self.components = {}

    def register(self, name, component):
        """Register a UI component with the mediator."""
        self.components[name] = component

    def notify(self, sender, event, data=None):
        """Handle communication between components."""
        if event == "password_created":
            # Notify SavedPasswords component to refresh its list
            if "SavedPasswords" in self.components:
                self.components["SavedPasswords"].update_password_list(data)
            # Notify Dashboard component to refresh its view
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)

        elif event == "password_deleted":
            # Notify SavedPasswords component to remove the password
            if "SavedPasswords" in self.components:
                self.components["SavedPasswords"].remove_password(data)
            # Notify Dashboard component to update its view
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)

        elif event == "password_updated":
            # Notify SavedPasswords component to update its list
            if "SavedPasswords" in self.components:
                self.components["SavedPasswords"].update_password(data)
            # Notify Dashboard component to refresh its view
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)

        else:
            raise KeyError(f"Unhandled event: {event}")
