from cryptography.fernet import Fernet

# Generate a key for encryption
ENCRYPTION_KEY = Fernet.generate_key()

# Print the key, copy it, and store it securely in your settings file
print(ENCRYPTION_KEY.decode())
