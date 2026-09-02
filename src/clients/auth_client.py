import logging

import httpx
from pydantic import BaseModel

from src.config.settings import Settings
from src.exceptions.external_api import ExternalApiAuthError
from src.utils.time import build_api_timestamp

logger = logging.getLogger(__name__)


class LoginResponse(BaseModel):
    message: str
    authorization: str


class AuthClient:
    def __init__(
        self,
        settings: Settings,
        client: httpx.Client,
    ) -> None:
        self._settings = settings
        self._client = client

    def login(self) -> str:
        logger.info("Iniciando autenticación contra la API externa")

        response = self._client.post(
            "/auth/login",
            headers={
                "accept": "*/*",
                "x-api-key": self._settings.api_key,
                "x-canal": self._settings.api_channel,
                "x-timestamp": build_api_timestamp(),
                "Content-Type": "application/json",
            },
            json={
                "email": self._settings.api_email,
                "password": self._settings.api_password,
            },
        )

        if response.status_code != 200:
            logger.error(
                "El login falló. HTTP %s",
                response.status_code,
            )

            raise ExternalApiAuthError(
                f"El login contra la API externa falló con HTTP {response.status_code}."
            )

        try:
            payload = LoginResponse.model_validate(
                response.json(),
            )
        except Exception as exc:
            raise ExternalApiAuthError(
                "La respuesta del login no tiene el formato esperado."
            ) from exc

        logger.info("Autenticación exitosa")

        return payload.authorization
