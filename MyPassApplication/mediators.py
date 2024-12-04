from .observer_registry import Observer

class UIMediator:
   

    def __init__(self):
        self.components = {}

    def register(self, name, component):
       
        self.components[name] = component

    def notify(self, sender, event, data=None):
        
        if sender in self.components:
            print(f"Mediator: Received event '{event}' from '{sender}' with data {data}")
        
        # Event handling for various entities
        if event in ("password_created", "password_deleted", "password_updated"):
            self._handle_password_event(event, data)

        elif event in ("identity_created", "identity_deleted", "identity_updated"):
            self._handle_identity_event(event, data)

        elif event in ("credit_card_created", "credit_card_deleted", "credit_card_updated"):
            self._handle_credit_card_event(event, data)

        elif event in ("secure_note_created", "secure_note_deleted", "secure_note_updated"):
            self._handle_secure_note_event(event, data)

        else:
            print(f"Unhandled event: {event}")

    def _handle_password_event(self, event, data):
       
        if event == "password_created":
            if "SavedPasswords" in self.components:
                self.components["SavedPasswords"].add_password(data)
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)
        elif event == "password_deleted":
            if "SavedPasswords" in self.components:
                self.components["SavedPasswords"].remove_password(data)
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)
        elif event == "password_updated":
            if "SavedPasswords" in self.components:
                self.components["SavedPasswords"].update_password(data)
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)

    def _handle_identity_event(self, event, data):
       
        if event == "identity_created":
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)
        elif event == "identity_deleted":
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)
        elif event == "identity_updated":
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)

    def _handle_credit_card_event(self, event, data):
       
        if event == "credit_card_created":
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)
        elif event == "credit_card_deleted":
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)
        elif event == "credit_card_updated":
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)

    def _handle_secure_note_event(self, event, data):
        
        if event == "secure_note_created":
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)
        elif event == "secure_note_deleted":
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)
        elif event == "secure_note_updated":
            if "Dashboard" in self.components:
                self.components["Dashboard"].refresh_dashboard(data)
