from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from MyPassApplication.models import CreditCard, Identity
from django.contrib.auth.models import User
from datetime import timedelta
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Checks for upcoming expirations and notifies users'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        upcoming_date = today + timedelta(days=30)  # Notify if expiration is within 30 days

        # Check Credit Cards
        expiring_creditcards = CreditCard.objects.filter(expiration_date__lte=upcoming_date)
        for card in expiring_creditcards:
            user = card.user
            # Send notification to user
            send_mail(
                'Credit Card Expiration Notice',
                f'Dear {user.username}, your credit card ending in {card.card_number[-4:]} is expiring soon.',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )

        # Check Passports
        expiring_passports = Identity.objects.filter(
            passport_expiration_date__lte=upcoming_date
        )
        for identity in expiring_passports:
            user = identity.user
            send_mail(
                'Passport Expiration Notice',
                f'Dear {user.username}, your passport is expiring soon.',
                'from@example.com',
                [user.email],
                fail_silently=False,
            )


         # Driver's License Expirations
        expiring_licenses = Identity.objects.filter(
            license_expiration_date__lte=upcoming_date, license_expiration_date__gte=today
        )
        for identity in expiring_licenses:
            user = identity.user
            send_mail(
                'Driver\'s License Expiration Notice',
                f'Dear {user.username},\n\nYour driver\'s license associated with your identity record is expiring on {identity.license_expiration_date}. Please renew it to keep your records up to date.\n\nBest regards,\nMyPass Team',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        self.stdout.write(self.style.SUCCESS('Expiration checks completed and notifications sent.'))
