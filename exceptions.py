from fastapi import HTTPException

# TODO : Define custom exceptions here as needed


class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=401, detail=detail, headers={"WWW-Authenticate": "Bearer"}
        )
