from .observer_registry import Observer

class SavedPasswords(Observer):
    def __init__(self, mediator):
        self.mediator = mediator

    def update_password_list(self, data):
        print(f"SavedPasswords: Updated with new data: {data}")
        # inform the mediator about changes
        self.mediator.notify("SavedPasswords", "password_updated", data)

    def update(self, event, data):
        if event == "password_created":
            self.update_password_list(data)
        elif event == "password_deleted":
            print(f"SavedPasswords: Removed password data: {data}")
        else:
            print(f"SavedPasswords: Unhandled event: {event}")


class Dashboard(Observer):
    def __init__(self, mediator):
        self.mediator = mediator

    def refresh_dashboard(self, data):
        print(f"Dashboard: Refreshed with data: {data}")
        # inform the mediator about changes
        self.mediator.notify("Dashboard", "dashboard_updated", data)

    def update(self, event, data):
        if event in ("password_created", "password_deleted"):
            self.refresh_dashboard(data)
        else:
            print(f"Dashboard: Unhandled event: {event}")
