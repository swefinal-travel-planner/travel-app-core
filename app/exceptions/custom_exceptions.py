class AppException(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

class ValidationError(AppException):
    def __init__(self, message="Validation error"):
        super().__init__(message, status_code=400)

class NotFoundError(AppException):
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)
