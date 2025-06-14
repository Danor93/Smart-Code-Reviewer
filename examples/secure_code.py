# Example: Secure and well-written code

import hashlib
import os
import secrets
from typing import List, Optional


class SecurePasswordManager:
    """
    A secure password manager implementation demonstrating best practices.
    """

    def __init__(self):
        self.salt = os.urandom(32)  # Generate random salt

    def hash_password(self, password: str) -> str:
        """
        Hash a password using PBKDF2 with SHA-256.

        Args:
            password: The password to hash

        Returns:
            The hashed password as a hex string
        """
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), self.salt, 100000).hex()  # 100k iterations

    def generate_secure_password(self, length: int = 16) -> str:
        """
        Generate a cryptographically secure random password.

        Args:
            length: Desired password length (minimum 8)

        Returns:
            A secure random password

        Raises:
            ValueError: If length is less than 8
        """
        if length < 8:
            raise ValueError("Password length must be at least 8 characters")

        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def validate_password_strength(self, password: str) -> dict:
        """
        Validate password strength against security requirements.

        Args:
            password: Password to validate

        Returns:
            Dictionary with validation results
        """
        result = {"valid": True, "score": 0, "requirements": []}

        if len(password) >= 12:
            result["score"] += 2
        elif len(password) >= 8:
            result["score"] += 1
        else:
            result["valid"] = False
            result["requirements"].append("Minimum 8 characters required")

        if any(c.isupper() for c in password):
            result["score"] += 1
        else:
            result["requirements"].append("At least one uppercase letter required")

        if any(c.islower() for c in password):
            result["score"] += 1
        else:
            result["requirements"].append("At least one lowercase letter required")

        if any(c.isdigit() for c in password):
            result["score"] += 1
        else:
            result["requirements"].append("At least one digit required")

        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            result["score"] += 1
        else:
            result["requirements"].append("At least one special character required")

        return result


# Example usage
if __name__ == "__main__":
    manager = SecurePasswordManager()

    # Generate a secure password
    secure_password = manager.generate_secure_password(16)
    print(f"Generated password: {secure_password}")

    # Validate the password
    validation = manager.validate_password_strength(secure_password)
    print(f"Password validation: {validation}")

    # Hash the password
    hashed = manager.hash_password(secure_password)
    print(f"Hashed password: {hashed[:32]}...")
