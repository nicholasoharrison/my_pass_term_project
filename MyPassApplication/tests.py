from django.test import TestCase

# Create your tests here.
from cryptography.fernet import Fernet

# Use the key from your settings or hardcode it for testing
key = b'ztPF3wqDiNOxcmSQQa-C4-TGAXavFwjtPnUsTiLskZI='  # replace this with the key you're using

cipher_suite = Fernet(key)

# Encrypt a test password
password = "MySecretPassword"
encrypted_password = cipher_suite.encrypt(password.encode())
print(f"Encrypted password: {encrypted_password}")

# Decrypt the test password
decrypted_password = cipher_suite.decrypt(encrypted_password).decode()
print(f"Decrypted password: {decrypted_password}")

