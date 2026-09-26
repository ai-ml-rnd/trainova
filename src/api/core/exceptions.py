"""Custom exceptions for the API."""


class ForgeException(Exception):
    """Base exception for all Forge errors."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(ForgeException):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str):
        self.resource = resource
        self.identifier = identifier
        super().__init__(
            f"{resource} with id {identifier} not found",
            status_code=404,
        )


class ValidationError(ForgeException):
    """Validation error."""

    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error on field '{field}': {message}", status_code=422)


class AuthError(ForgeException):
    """Authentication error."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status_code=401)


class PermissionError(ForgeException):
    """Authorization error."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, status_code=403)


class ConflictError(ForgeException):
    """Conflict error."""

    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, status_code=409)


class ServiceError(ForgeException):
    """External service error."""

    def __init__(self, service: str, message: str):
        self.service = service
        self.message = message
        super().__init__(f"Service '{service}' error: {message}", status_code=503)
