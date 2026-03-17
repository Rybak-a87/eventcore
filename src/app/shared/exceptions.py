from fastapi import HTTPException, status


class InvalidCredentials(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotAuthenticated(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        
class UserAlreadyTaken(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already taken",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        
class PasswordMustBeDifferent(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be different",
            headers={"WWW-Authenticate": "Bearer"},
        )


class PasswordMustBeDifferent(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be different",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidToken(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


class WeakPassword(HTTPException):
    def __init__(self, text_error):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(text_error),
            headers={"WWW-Authenticate": "Bearer"},
        )


class EventNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
            headers={"WWW-Authenticate": "Bearer"},
        )


class EventAlreadyExists(HTTPException):
    def __init__(self, title, type_name):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event {title} in category {type_name} already exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

# class NotAuthenticatedAdmin(HTTPException):
#     def __init__(self):
#         super().__init__(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Admin privileges required",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
