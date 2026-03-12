import re


class WeakPasswordError(Exception):
    class WeakPassword(Exception):
        def __init__(self, message: str):
            self.message = message
            super().__init__(message)


class PasswordPolicy:
    CHECKS = {
        "uppercase letter": re.compile(r"[A-Z]"),
        "lowercase letter": re.compile(r"[a-z]"),
        "digit": re.compile(r"\d"),
        "special character": re.compile(r"[!@#$%^&*(),.?'\":{}|<>]")
    }
    MIN_LENGTH = 8

    @classmethod
    def validate(cls, password: str) -> None:
        errors = []

        if len(password) < cls.MIN_LENGTH:
            errors.append(f"at least {cls.MIN_LENGTH} characters")

        for name, pattern in cls.CHECKS.items():
            if not pattern.search(password):
                errors.append(name)

        if errors:
            raise WeakPasswordError(
                "Password must contain: " + ", ".join(errors)
            )
