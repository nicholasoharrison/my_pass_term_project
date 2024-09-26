from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User



class SessionManager: # follows Singleton pattern to only allow one session at a time
    _instance = None 

    def __new__(cls):
        if cls._instance is None: # only creates a new instance of SessionManager if there is NONE
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.initialized = False 
        return cls._instance # otherwise returns the current instance of SessionManager

    def __init__(self): # constructor (that is not called due to Singleton pattern)
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
    
    def update_last_activity(self):
        self.request.session['last_activity'] = timezone.now().isoformat() # gets the time of the activity that was last performed

    def has_timed_out(self):
        last_activity = self.request.session.get('last_activity') # retrieves the time of the last activity performed
        if last_activity:
            last_activity_time = timezone.datetime.fromisoformat(last_activity)
            return timezone.now() - last_activity_time > timedelta(minutes=1) # if the time of th elast activity was more than a minute ago
                                                                              # true is returned for timeout, user will be sent back to login
        return False



class SecurityQuestion(models.Model): # model to store the answer to their 3 security questions
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    q1Answer = models.CharField(max_length=100)
    q2Answer = models.CharField(max_length=100)
    q3Answer = models.CharField(max_length=100)


