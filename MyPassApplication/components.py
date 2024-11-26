# components.py
class SavedPasswords:
    def __init__(self, mediator):
        self.mediator = mediator

    def update_password_list(self, data):
        print(f"SavedPasswords: Updating password list with data: {data}")

    def remove_password(self, data):
        print(f"SavedPasswords: Removing password with data: {data}")

class Dashboard:
    def __init__(self, mediator):
        self.mediator = mediator

    def refresh_dashboard(self, data):
        print(f"Dashboard: Refreshing dashboard with data: {data}")

