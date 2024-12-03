from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now
from datetime import timedelta
from .models import CreditCard, Identity, Notification, Account
from .observer_registry import ObserverRegistry
import logging

# Initialize logger
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Account)
def handle_password_created(sender, instance, created, **kwargs):
    """
    Notify observers when a new password account is created.
    """
    if created:
        ObserverRegistry.notify_observers(
            event="password_created",
            data={"id": instance.id, "name": instance.name}
        )

@receiver(post_delete, sender=Account)
def handle_password_deleted(sender, instance, **kwargs):  
   # Notify observers when a password account is deleted. 
    ObserverRegistry.notify_observers(
        event="password_deleted",
        data={"id": instance.id, "name": instance.name}
    )
    logger.info(f"Observer notified for password_deleted: {instance.id}, {instance.name}")

def create_notification(user, message):   
   # Utility function to create notifications, avoiding duplicates.   
    if not Notification.objects.filter(user=user, message=message).exists():
        Notification.objects.create(user=user, message=message)

@receiver(post_save, sender=CreditCard)
def notify_credit_card_expiration(sender, instance, **kwargs):
      # Notify the user if their credit card is about to expire.
    try:
        if not instance.expiration_date:
            return

        upcoming_date = now().date() + timedelta(days=30)
        if instance.expiration_date <= upcoming_date:
            message = f"Your credit card ending in {instance.card_number[-4:]} is expiring soon."
            create_notification(user=instance.user, message=message)
    except Exception as e:
        logger.error(f"Error notifying credit card expiration: {e}")

@receiver(post_save, sender=Identity)
def notify_identity_expiration(sender, instance, **kwargs):   
   # Notify the user if their passport or driver's license is about to expire. 
    try:
        upcoming_date = now().date() + timedelta(days=30)

        # Passport expiration notification
        if instance.passport_expiration_date and instance.passport_expiration_date <= upcoming_date:
            if not instance.passport_notified:
                message = f"Your passport is expiring on {instance.passport_expiration_date}."
                create_notification(user=instance.user, message=message)
                instance.passport_notified = True
                instance.save(update_fields=["passport_notified"])

        # License expiration notification
        if instance.license_expiration_date and instance.license_expiration_date <= upcoming_date:
            if not instance.license_notified:
                message = f"Your driver’s license is expiring on {instance.license_expiration_date}."
                create_notification(user=instance.user, message=message)
                instance.license_notified = True
                instance.save(update_fields=["license_notified"])
    except Exception as e:
        logger.error(f"Error notifying identity expiration: {e}")
