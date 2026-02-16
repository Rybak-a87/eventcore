import re
from dataclasses import dataclass

from pydantic import EmailStr


class WeakPasswordError(Exception):
    pass


@dataclass
class PasswordEntity:
    email: EmailStr
    password: str

    def validate_password(self) -> None:
        checks = {
            "uppercase letter": r"[A-Z]",
            "lowercase letter": r"[a-z]",
            "digit": r"\d",
            "special character": r"[!@#$%^&*(),.?'\":{}|<>]"
        }
        for error_name, pattern in checks.items():
            if not re.search(pattern, self.password):
                raise WeakPasswordError(f"Password must contain at least one {error_name}")
        # if self.password == self.email:
        #     raise WeakPasswordError("Email and password should not be the same.")
