import logging

import httpx
from pydantic import BaseModel, ConfigDict, Field

from src.auth.token_manager import TokenManager
from src.config.settings import Settings
from src.exceptions.external_api import (
    ExternalApiError,
    ExternalApiForbiddenError,
    ExternalApiNotFoundError,
    ExternalApiRateLimitError,
    ExternalApiServerError,
    ExternalApiUnauthorizedError,
)
from src.utils.time import build_api_timestamp

logger = logging.getLogger(__name__)


class ItemsMeta(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )

    page: int | None = None
    limit: int | None = None

    total_rows: int | None = Field(
        default=None,
        alias="totalRows",
    )

    total_pages: int | None = Field(
        default=None,
        alias="totalPages",
    )


class ItemCriterio(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )

    id_plan: str | None = Field(
        default=None,
        alias="idPlan",
    )

    descripcion_plan: str | None = Field(
        default=None,
        alias="descripcionPlan",
    )

    id_criterio: str | None = Field(
        default=None,
        alias="idCriterio",
    )

    descripcion_criterio: str | None = Field(
        default=None,
        alias="descripcionCriterio",
    )


class ItemDescripcionTecnica(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )

    id_descripcion_tecnica: str | None = Field(
        default=None,
        alias="idDescripcionTecnica",
    )

    descripcion_tecnica: str | None = Field(
        default=None,
        alias="descripcionTecnica",
    )

    campo: str | None = None

    valor: str | None = None


class Item(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )

    id_compania: int | None = Field(
        default=None,
        alias="idCompania",
    )

    item: int | None = None

    descripcion_item: str | None = Field(
        default=None,
        alias="descripcionItem",
    )

    descripcion_corta_item: str | None = Field(
        default=None,
        alias="descripcionCortaItem",
    )

    referencia_alterna: str | None = Field(
        default=None,
        alias="referenciaAlterna",
    )

    codigo_barra_principal: str | None = Field(
        default=None,
        alias="codigoBarraPrincipal",
    )

    unidad_inventario: str | None = Field(
        default=None,
        alias="unidadInventario",
    )

    id_codigo_unspsc: str | None = Field(
        default=None,
        alias="idCodigoUnspsc",
    )

    descripcion_codigo_unspsc: str | None = Field(
        default=None,
        alias="descripcionCodigoUnspsc",
    )

    criterios: list[ItemCriterio] = Field(
        default_factory=list,
    )

    descripciones_tecnicas: list[ItemDescripcionTecnica] = Field(
        default_factory=list,
        alias="descripcionesTecnicas",
    )


class ItemsResponse(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
    )

    meta: ItemsMeta
    data: list[Item]


class ItemsClient:
    def __init__(
        self,
        settings: Settings,
        client: httpx.Client,
        token_manager: TokenManager,
    ) -> None:
        self._settings = settings
        self._client = client
        self._token_manager = token_manager

    def get_items(self) -> list[Item]:
        token = self._token_manager.get_token()

        if token is None:
            raise ExternalApiUnauthorizedError(
                "No se pudo obtener el token de autenticación."
            )

        response = self._request(token)

        if response.status_code == 401:
            logger.warning(
                "La API rechazó el token con HTTP 401. "
                "Se renovará el token y se reintentará una vez."
            )

            self._token_manager.invalidate()

            token = self._token_manager.get_token()

            if token is None:
                raise ExternalApiUnauthorizedError(
                    "No se pudo obtener el token de autenticación tras renovar."
                )

            response = self._request(token)

            if response.status_code == 401:
                raise ExternalApiUnauthorizedError(
                    "La API continúa devolviendo HTTP 401 después de renovar el token."
                )

        self._raise_for_error(response)

        raw_data = response.json()

        try:
            payload = ItemsResponse.model_validate(raw_data)
        except Exception as exc:
            raise ExternalApiError(
                "La respuesta del endpoint de items no tiene el formato esperado."
            ) from exc

        logger.info(
            "Items obtenidos correctamente: %s",
            len(payload.data),
        )

        return payload.data

    def _request(
        self,
        token: str,
    ) -> httpx.Response:
        return self._client.get(
            "/connekta/items",
            params={
                "idCompania": self._settings.company_id,
            },
            headers={
                "accept": "application/json",
                "x-api-key": self._settings.api_key,
                "Authorization": f"Bearer {token}",
                "x-canal": self._settings.api_channel,
                "x-timestamp": build_api_timestamp(),
            },
        )

    @staticmethod
    def _raise_for_error(
        response: httpx.Response,
    ) -> None:
        if response.is_success:
            return

        match response.status_code:
            case 401:
                raise ExternalApiUnauthorizedError("La API externa rechazó el token.")

            case 403:
                raise ExternalApiForbiddenError(
                    "La API externa rechazó la solicitud por permisos."
                )

            case 404:
                raise ExternalApiNotFoundError("El endpoint de items no existe.")

            case 429:
                raise ExternalApiRateLimitError(
                    "La API externa está limitando las solicitudes."
                )

            case 500 | 502 | 503 | 504:
                raise ExternalApiServerError(
                    f"La API externa devolvió HTTP {response.status_code}."
                )

            case _:
                raise ExternalApiError(
                    f"La API externa devolvió HTTP {response.status_code}."
                )
