
class BaseApplicationError(Exception):
    """Base exception class for application errors."""
    def __init__(self, message="An error occurred", status_code=500, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(BaseApplicationError):
    """Raised when validation fails."""
    def __init__(self, message="Validation failed", field=None):
        self.field = field
        super().__init__(message, status_code=400, error_code="validation_error")


class AuthenticationError(BaseApplicationError):
    """Raised when authentication fails."""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, status_code=401, error_code="authentication_error")


class AuthorizationError(BaseApplicationError):
    """Raised when authorization fails."""
    def __init__(self, message="Access denied"):
        super().__init__(message, status_code=403, error_code="authorization_error")


class NotFoundError(BaseApplicationError):
    """Raised when a resource is not found."""
    def __init__(self, message="Resource not found", resource_type=None):
        self.resource_type = resource_type
        super().__init__(message, status_code=404, error_code="not_found_error")


class DatabaseError(BaseApplicationError):
    """Raised when database operations fail."""
    def __init__(self, message="Database operation failed", operation=None):
        self.operation = operation
        super().__init__(message, status_code=500, error_code="database_error")


class ExpertSystemError(BaseApplicationError):
    """Raised when expert system operations fail."""
    def __init__(self, message="Expert system error"):
        super().__init__(message, status_code=500, error_code="expert_system_error")


class InvalidRequestError(BaseApplicationError):
    """Raised when request data is invalid."""
    def __init__(self, message="Invalid request", missing_param=None):
        self.missing_param = missing_param
        super().__init__(message, status_code=400, error_code="invalid_request")


class SportNotSupportedError(BaseApplicationError):
    """Raised when an unsupported sport is requested."""
    def __init__(self, sport=None):
        message = f"Sport '{sport}' is not supported" if sport else "Sport not supported"
        super().__init__(message, status_code=400, error_code="sport_not_supported")


class SessionNotFoundError(NotFoundError):
    """Raised when a chat session is not found."""
    def __init__(self, session_id=None):
        message = f"Session {session_id} not found" if session_id else "Session not found"
        super().__init__(message, resource_type="session")


class SessionInactiveError(BaseApplicationError):
    """Raised when trying to use an inactive session."""
    def __init__(self, session_id=None):
        message = f"Session {session_id} is inactive" if session_id else "Session is inactive"
        super().__init__(message, status_code=400, error_code="session_inactive")


class NoActiveSportError(BaseApplicationError):
    """Raised when no sport has been selected."""
    def __init__(self):
        super().__init__("Please select a sport first", status_code=400, error_code="no_active_sport")
