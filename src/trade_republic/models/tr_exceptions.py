from typing import Any


class TradeRepublicError(Exception):
    """Base exception for Trade Republic SDK

    All custom exceptions inherit from this class.
    """

    def __init__(self, message: str, **kwargs):
        self.message = message
        self.context = kwargs
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


# ============================================================================
# Authentication & Session Errors
# ============================================================================


class AuthenticationError(TradeRepublicError):
    """Raised when authentication fails

    Examples:
        - Invalid phone number or PIN
        - Session token expired
        - 2FA code is incorrect
    """

    pass


class SessionExpiredError(AuthenticationError):
    """Raised when session token has expired"""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when provided credentials are invalid"""

    pass


# ============================================================================
# Validation Errors
# ============================================================================


class ValidationError(TradeRepublicError):
    """Raised when data validation fails"""

    pass


class InvalidISINError(ValidationError):
    """Raised when ISIN format is invalid

    ISIN must be 12 alphanumeric characters.
    """

    def __init__(self, isin: str, message: str = ""):
        if not message:
            message = f"Invalid ISIN format: '{isin}'. ISIN must be 12 alphanumeric characters."
        self.isin = isin
        super().__init__(message)


class InvalidExchangeError(ValidationError):
    """Raised when exchange code is invalid"""

    def __init__(self, exchange: str, valid_exchanges: list | None = None):
        message = f"Invalid exchange: '{exchange}'"
        if valid_exchanges:
            message += f". Valid exchanges: {', '.join(valid_exchanges)}"
        self.exchange = exchange
        super().__init__(message)


class InvalidOrderError(ValidationError):
    """Raised when order parameters are invalid"""

    def __init__(self, message: str, order_params: dict[str, Any] | None = None):
        self.order_params = order_params or {}
        super().__init__(message)


class InvalidConfigurationError(ValidationError):
    """Raised when configuration is invalid"""

    pass


# ============================================================================
# API & Network Errors
# ============================================================================


class APIError(TradeRepublicError):
    """Raised when API returns an error

    Attributes:
        status_code: HTTP status code if applicable
        response_data: Full API response data
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(message, status_code=status_code, response_data=response_data)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded

    Attributes:
        retry_after: Seconds to wait before retrying
    """

    def __init__(self, message: str = "", retry_after: int | None = None, **kwargs):
        if message is None:
            message = "Rate limit exceeded"
            if retry_after:
                message += f". Retry after {retry_after} seconds."
        self.retry_after = retry_after
        super().__init__(message, **kwargs)


class WebSocketError(APIError):
    """Raised when WebSocket connection fails"""

    pass


class WebSocketConnectionError(WebSocketError):
    """Raised when WebSocket connection cannot be established"""

    pass


class WebSocketTimeoutError(WebSocketError):
    """Raised when WebSocket request times out"""

    pass


class NetworkError(APIError):
    """Raised when network communication fails"""

    pass


class ConnectionTimeoutError(NetworkError):
    """Raised when connection times out"""

    pass


# ============================================================================
# Data & Response Errors
# ============================================================================


class DataError(TradeRepublicError):
    """Raised when data processing fails"""

    pass


class MissingDataError(DataError):
    """Raised when expected data is missing from response"""

    def __init__(self, field: str, context: str = ""):
        message = f"Missing required field: '{field}'"
        if context:
            message += f" (context: {context})"
        self.field = field
        super().__init__(message)


class InvalidDataError(DataError):
    """Raised when data format/content is invalid"""

    pass


class InstrumentNotFoundError(DataError):
    """Raised when instrument/security cannot be found"""

    def __init__(self, isin: str = "", identifier: str = ""):
        if isin:
            message = f"Instrument not found: ISIN '{isin}'"
        elif identifier:
            message = f"Instrument not found: '{identifier}'"
        else:
            message = "Instrument not found"
        super().__init__(message)


class OrderNotFoundError(DataError):
    """Raised when order cannot be found"""

    def __init__(self, order_id: str):
        super().__init__(f"Order not found: '{order_id}'")


class PortfolioError(DataError):
    """Raised when portfolio-related operation fails"""

    pass


# ============================================================================
# File & I/O Errors
# ============================================================================


class FileOperationError(TradeRepublicError):
    """Raised when file operation fails"""

    pass


class FileNotFoundSDKError(FileOperationError):
    """Raised when required file is not found.

    Named FileNotFoundSDKError to avoid shadowing the built-in FileNotFoundError.
    """

    def __init__(self, filepath: str):
        super().__init__(f"File not found: '{filepath}'")


class FileWriteError(FileOperationError):
    """Raised when file write operation fails"""

    def __init__(self, filepath: str, reason: str = ""):
        message = f"Failed to write file: '{filepath}'"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


# ============================================================================
# Service Errors
# ============================================================================


class ServiceError(TradeRepublicError):
    """Raised when service operation fails"""

    pass


class ServiceInitializationError(ServiceError):
    """Raised when service cannot be initialized"""

    pass


class ServiceNotAvailableError(ServiceError):
    """Raised when service is not available"""

    pass
