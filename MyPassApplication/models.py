from django.db import models


class SessionManager:
    _instance = None 

    def __new__(cls):
        if cls._instance is None: 
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.initialized = False 
        return cls._instance 

    def __init__(self):
        if not self.initialized:
            self.current_user = None  
            self.initialized = True  

    def set_request(self, request):
        self.request = request 

    def login(self, user):
        self.current_user = user  
        self.request.session['is_authenticated'] = True 

    def logout(self):
        self.current_user = None  
        self.request.session.flush() 

    def is_authenticated(self):
        return self.request.session.get('is_authenticated', False)

    def get_current_user(self):
        return self.current_user