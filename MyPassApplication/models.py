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
            cls._instance.current_user = None
        return cls._instance # otherwise returns the current instance of SessionManager (so that only one can be created)

    def set_request(self, request):
        self.request = request 

    # indicates that a user is logged in and authenticated
    #store the user's ID in the session. 
    # Then, in the get_current_user method, retrieve the user from the database using the ID stored in the session.
    def login(self, user):
      self.request.session['is_authenticated'] = True
      self.request.session['user_id'] = user.id


    # removes the user from the session and clears session data
    def logout(self):
       self.request.session.flush()


    def is_authenticated(self):
        return self.request.session.get('is_authenticated', False)

    def get_current_user(self):
      user_id = self.request.session.get('user_id')
      if user_id:
            return User.objects.get(id=user_id)
      return None

    
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


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vault')
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} : {self.password}"    

#vault functionality
class Login(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    site_name = models.CharField(max_length=255)
    site_url = models.URLField(blank=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.site_name} ({self.username})"

class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cardholder_name = models.CharField(max_length=255)
    card_number = models.CharField(max_length=16)
    expiration_date = models.DateField()
    cvv = models.CharField(max_length=4)
    billing_address = models.TextField(blank=True)
    # def __str__(self):
    #     return f"Card ending in {self.card_number[-4:]}"

#added as part of notification system
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.check_expiration()

    def check_expiration(self):
        upcoming_date = timezone.now().date() + timedelta(days=30)
        if self.expiration_date and self.expiration_date <= upcoming_date:
            # Create a notification
            message = f"Your credit card ending in {self.card_number[-4:]} is expiring on {self.expiration_date}."
            Notification.objects.create(user=self.user, message=message)



class Identity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=20, blank=True)
    license_number = models.CharField(max_length=20, blank=True)
    social_security_number = models.CharField(max_length=11, blank=True)
    #added  to check expirations
    passport_notified = models.BooleanField(default=False)
    license_notified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

#added as part of notification system
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.check_passport_expiration()
        self.check_license_expiration()

        # def __str__(self):
        #   return self.full_name

    def check_passport_expiration(self):
        upcoming_date = timezone.now().date() + timedelta(days=30)
        if self.passport_expiration_date and self.passport_expiration_date <= upcoming_date:
            message = f"Your passport is expiring on {self.passport_expiration_date}."
            Notification.objects.create(user=self.user, message=message)

    def check_license_expiration(self):
        upcoming_date = timezone.now().date() + timedelta(days=30)
        if self.license_expiration_date and self.license_expiration_date <= upcoming_date:
            message = f"Your driver's license is expiring on {self.license_expiration_date}."
            Notification.objects.create(user=self.user, message=message)



class SecureNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.title

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"        
    


