class ExternalApiError(Exception):
    """Error general al comunicarse con una API externa."""


class ExternalApiAuthError(ExternalApiError):
    """Error durante la autenticación contra una API externa."""


class ExternalApiUnauthorizedError(ExternalApiError):
    """La API externa rechazó las credenciales o el token."""


class ExternalApiForbiddenError(ExternalApiError):
    """La API externa rechazó la operación por permisos."""


class ExternalApiNotFoundError(ExternalApiError):
    """El endpoint o recurso solicitado no existe."""


class ExternalApiRateLimitError(ExternalApiError):
    """La API externa está limitando las solicitudes."""


class ExternalApiServerError(ExternalApiError):
    """La API externa devolvió un error temporal del servidor."""
