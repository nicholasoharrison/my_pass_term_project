from abc import ABC, abstractmethod
import random
import string
from .models import Password

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
        return password_value


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