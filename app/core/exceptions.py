class MusicErrorServiceException(Exception):
    """Base class for all musical error service exceptions"""
    def __init__(self, message: str, code: str = "500"):
        self.message = message
        self.code = code
        super().__init__(message)

class DatabaseConnectionException(MusicErrorServiceException):
    """Database connection error"""
    def __init__(self, message: str = "Database connection error"):
        super().__init__(message, "500")
        
class ValidationException(MusicErrorServiceException):
    """Data validation error"""
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, "400")