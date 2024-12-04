from datetime import date, timedelta
from unittest.mock import Mock
from django.test import TestCase

# # Create your tests here.
# from cryptography.fernet import Fernet

# # Use the key from your settings or hardcode it for testing
# key = b'ztPF3wqDiNOxcmSQQa-C4-TGAXavFwjtPnUsTiLskZI='  # replace this with the key you're using

# cipher_suite = Fernet(key)

# # Encrypt a test password
# password = "MySecretPassword"
# encrypted_password = cipher_suite.encrypt(password.encode())
# print(f"Encrypted password: {encrypted_password}")

# # Decrypt the test password
# decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
# print(f"Decrypted password: {decrypted_password}")


#test case for expiration dates
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from MyPassApplication.models import Identity, User

class IdentityExpirationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser", password="password123")

    @patch('MyPassApplication.models.ObserverRegistry.notify_observers')
    def test_passport_expiration_notification(self, mock_notify):
        # Create an identity with a passport expiration date in the future
        identity = Identity.objects.create(
            user=self.user,
            full_name="Future Passport User",
            passport_expiration_date=timezone.now().date() + timedelta(days=31)
        )
        identity.check_passport_expiration()
        mock_notify.assert_not_called()  # No notification for a future expiration date

        # Update passport expiration date to within 30 days
        identity.passport_expiration_date = timezone.now().date() + timedelta(days=5)
        identity.passport_notified = False
        identity.save()
        identity.check_passport_expiration()
        mock_notify.assert_called_with(
            event="passport_expiring",
            data={"user_id": self.user.id, "expiration_date": identity.passport_expiration_date},
        )

    @patch('MyPassApplication.models.ObserverRegistry.notify_observers')
    def test_license_expiration_notification(self, mock_notify):
        # Create an identity with a license expiration date in the future
        identity = Identity.objects.create(
            user=self.user,
            full_name="Future License User",
            license_expiration_date=timezone.now().date() + timedelta(days=31)
        )
        identity.check_license_expiration()
        mock_notify.assert_not_called()  # No notification for a future expiration date

        # Update license expiration date to within 30 days
        identity.license_expiration_date = timezone.now().date() + timedelta(days=5)
        identity.license_notified = False
        identity.save()
        identity.check_license_expiration()
        mock_notify.assert_called_with(
            event="license_expiring",
            data={"user_id": self.user.id, "expiration_date": identity.license_expiration_date},
        )
