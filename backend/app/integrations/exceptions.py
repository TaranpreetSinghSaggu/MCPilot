class IntegrationError(Exception):
    """Base exception for external integration failures."""


class IntegrationAuthenticationError(IntegrationError):
    """Raised when authentication with an external platform fails."""


class IntegrationNotFoundError(IntegrationError):
    """Raised when an external resource does not exist."""


class IntegrationRateLimitError(IntegrationError):
    """Raised when an external platform rate limit is exceeded."""


class IntegrationRequestError(IntegrationError):
    """Raised when an external API request fails."""