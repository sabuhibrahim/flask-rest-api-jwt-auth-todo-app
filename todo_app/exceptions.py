from typing import Optional


class AuthorizationException(Exception):
    status_code: int = 401

    def __init__(self, message: Optional[str] = None, data: Optional[dict] = None):
        super().__init__(message or "Unauthorized")
        self.message = message or "Unauthorized"
        self.data = data

    def dict(self):
        return {
            "message": self.message,
            "data": self.data,
        }


class NotFoundException(Exception):
    status_code: int = 404

    def __init__(self, message: Optional[str] = None, data: Optional[dict] = None):
        super().__init__(message or "Not Found")
        self.message = message or "Not Found"
        self.data = data

    def dict(self):
        return {
            "message": self.message,
            "data": self.data,
        }


class BadRequestException(Exception):
    status_code: int = 400

    def __init__(self, message: Optional[str] = None, data: Optional[dict] = None):
        super().__init__(message or "Not Found")
        self.message = message or "Not Found"
        self.data = data

    def dict(self):
        return {
            "message": self.message,
            "data": self.data,
        }
