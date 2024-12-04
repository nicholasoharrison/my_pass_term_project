from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from .observer_registry import ObserverRegistry


class SessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._instance.initialized = False
            cls._instance.current_user = None
        return cls._instance

    def set_request(self, request):
        self.request = request

    def login(self, user):
        self.request.session['is_authenticated'] = True
        self.request.session['user_id'] = user.id

    def logout(self):
        self.request.session.flush()

    def is_authenticated(self):
        return self.request.session.get('is_authenticated', False)

    def get_current_user(self):
        user_id = self.request.session.get('user_id')
        if user_id:
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.request.session.flush()
                return None
        return None

    def update_last_activity(self):
        self.request.session['last_activity'] = timezone.now().isoformat()

    def has_timed_out(self):
        last_activity = self.request.session.get('last_activity')
        if last_activity:
            last_activity_time = timezone.datetime.fromisoformat(last_activity)
            return timezone.now() - last_activity_time > timedelta(minutes=1)
        return False


class SecurityQuestion(models.Model):
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
    password = models.CharField(max_length=100)  # Store encripted  password here
    suggested = models.BooleanField(default=False)  # New field to mark suggested passwords
    #created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} : {self.password}"
    
    def save(self, *args, **kwargs):
        created = self._state.adding  
        super().save(*args, **kwargs)
        if created:
            # Notify observers about the password creation
            ObserverRegistry.notify_observers(
                event="password_created",
                data={"id": self.id, "name": self.name}
            )


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

    def __str__(self):
        return f"Card ending in {self.card_number[-4:]}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.check_expiration()

    def check_expiration(self):
        upcoming_date = timezone.now().date() + timedelta(days=30)
        if self.expiration_date and self.expiration_date <= upcoming_date:
            # Notify observers about the credit card expiration
            ObserverRegistry.notify_observers(
                event="credit_card_expiring",
                data={"user_id": self.user.id, "card_number": self.card_number[-4:]}
            )


class Identity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField(null=True, blank=True)
    passport_number = models.CharField(max_length=20, blank=True)
    passport_expiration_date = models.DateField(null=True, blank=True, default=None)
    license_number = models.CharField(max_length=20, blank=True)
    license_expiration_date = models.DateField(null=True, blank=True, default=None)
    social_security_number = models.CharField(max_length=11, blank=True)
    passport_notified = models.BooleanField(default=False)
    license_notified = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.check_passport_expiration()
        self.check_license_expiration()

    def check_passport_expiration(self):
        upcoming_date = timezone.now().date() + timedelta(days=30)
        if self.passport_expiration_date and self.passport_expiration_date <= upcoming_date:
            if not self.passport_notified:
                # Notify observers about the passport expiration
                ObserverRegistry.notify_observers(
                    event="passport_expiring",
                    data={"user_id": self.user.id, "expiration_date": self.passport_expiration_date}
                )
                self.passport_notified = True
                self.save(update_fields=['passport_notified'])

    def check_license_expiration(self):
        upcoming_date = timezone.now().date() + timedelta(days=30)
        if self.license_expiration_date and self.license_expiration_date <= upcoming_date:
            if not self.license_notified:
                # Notify observers about the license expiration
                ObserverRegistry.notify_observers(
                    event="license_expiring",
                    data={"user_id": self.user.id, "expiration_date": self.license_expiration_date}
                )
                self.license_notified = True
                self.save(update_fields=['license_notified'])

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
