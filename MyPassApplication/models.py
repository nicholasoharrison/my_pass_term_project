from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from abc import ABC, abstractmethod
import random
import string


class SessionManager: # follows Singleton pattern to only allow one session at a time
    _instance = None 

    def __new__(cls):
        if cls._instance is None: # only creates a new instance of SessionManager if there is NONE
            cls._instance = super(SessionManager, cls).__new__(cls) # see link for reference line of code: https://medium.com/analytics-vidhya/how-to-create-a-thread-safe-singleton-class-in-python-822e1170a7f6
            cls._instance.initialized = False 
        return cls._instance # otherwise returns the current instance of SessionManager (so that only one can be created)

    def set_request(self, request):
        self.request = request 

    # indicates that a user is logged in and authenticated
    def login(self, user):
        self.current_user = user  
        self.request.session['is_authenticated'] = True 

    # removes the user from the session and clears session data
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
            return timezone.now() - last_activity_time > timedelta(minutes=1) # if the time of the last activity was more than a minute ago
                                                                              # true is returned for timeout, user will be sent back to login
        return False



class SecurityQuestion(models.Model): # model to store the answer to their 3 security questions
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_question')
    q1Answer = models.CharField(max_length=100)
    q2Answer = models.CharField(max_length=100)
    q3Answer = models.CharField(max_length=100)


class Password:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value
    


class PasswordBuilder:
    def __init__(self):
        self._length = 8
        self._use_uppercase = False
        self._use_lowercase = False
        self._use_numbers = False
        self._use_special_chars = False

    def set_length(self, length):
        """Set the length of the password."""
        self._length = length
        return self

    def include_uppercase(self):
        """Include uppercase letters in the password."""
        self._use_uppercase = True
        return self

    def include_lowercase(self):
        """Include lowercase letters in the password."""
        self._use_lowercase = True
        return self

    def include_numbers(self):
        """Include numbers in the password."""
        self._use_numbers = True
        return self

    def include_special_chars(self):
        """Include special characters in the password."""
        self._use_special_chars = True
        return self

    @abstractmethod
    def build_character_pool(self):
        """Define character pool based on password requirements."""
        pass

    def build(self):
        """Generate the password using the character pool."""
        self.build_character_pool()
        if not self.character_pool:
            raise ValueError("Character pool is empty; check builder configuration.")

        # Generate the password by selecting random characters from the pool
        password_value = ''.join(random.choice(self.character_pool) for _ in range(self._length))
        return Password(password_value)


class SimplePasswordBuilder(PasswordBuilder):
    def build_character_pool(self):
        """Set character pool for a simple password (e.g., lowercase only)."""
        self.character_pool = string.ascii_lowercase
        self.set_length(8)



class ComplexPasswordBuilder(PasswordBuilder):
    def build_character_pool(self):
        """Set character pool for a complex password (uppercase, lowercase, digits, special characters)."""
        self.character_pool = (
            string.ascii_uppercase +
            string.ascii_lowercase +
            string.digits +
            string.punctuation
        )
        self.set_length(12)



class PasswordDirector:
    def __init__(self, builder):
        self.builder = builder

    def create_password(self):
        """Generate the password by calling the builder's build method."""
        return self.builder.build()