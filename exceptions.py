from fastapi import HTTPException

# TODO : Define custom exceptions here as needed


class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"}
        )


class UserNotFoundError(HTTPException):
    def __init__(self, user_id):
        super().__init__(status_code=404, detail=f"User with ID {user_id} not found.")


class InvalidPasswordError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400, detail="The current password provided is incorrect."
        )


class PasswordMismatchError(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="The new passwords do not match.")


class UserAlreadyExistsError(HTTPException):
    def __init__(self, email):
        super().__init__(
            status_code=400, detail=f"User with email {email} already exists."
        )
