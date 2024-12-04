from .observer_registry import Observer

class SavedPasswords(Observer):
    def __init__(self, mediator):
        self.mediator = mediator

    def update_password_list(self, data):
        print(f"SavedPasswords: Updated with new data: {data}")
        # Inform the mediator about changes
        self.mediator.notify("SavedPasswords", "password_updated", data)

    def remove_password(self, data):
        print(f"SavedPasswords: Removed password data: {data}")
        # Inform the mediator about the removal
        #self.mediator.notify("SavedPasswords", "password_deleted", data)

    def add_password(self, data):
        print(f"SavedPasswords: Added password data: {data}")
        

    def update(self, event, data):
        if event == "password_created":
            self.add_password(data)
        elif event == "password_deleted":
            self.remove_password(data)
        elif event == "password_updated":
            self.update_password_list(data)
        else:
            print(f"SavedPasswords: Unhandled event: {event}")



class Dashboard(Observer):
    def __init__(self, mediator):
        self.mediator = mediator

    def refresh_dashboard(self, data):
        print(f"Dashboard: Refreshed with data: {data}")
        # Inform the mediator about changes
        self.mediator.notify("Dashboard", "dashboard_updated", data)

    def update(self, event, data):
        if event in ("password_created", "password_deleted", "password_updated"):
            self.refresh_dashboard(data)
        else:
            print(f"Dashboard: Unhandled event: {event}")
