from unittest.mock import MagicMock

import httpx
import pytest

from src.clients.items_client import ItemsClient
from src.config.settings import Settings
from src.exceptions.external_api import (
    ExternalApiError,
    ExternalApiForbiddenError,
    ExternalApiNotFoundError,
    ExternalApiRateLimitError,
    ExternalApiServerError,
    ExternalApiUnauthorizedError,
)

VALID_ITEMS_PAYLOAD = {
    "meta": {"page": 1, "limit": 50, "totalRows": 1, "totalPages": 1},
    "data": [
        {
            "idCompania": 1,
            "item": 100,
            "descripcionItem": "Item de prueba",
            "criterios": [],
            "descripcionesTecnicas": [],
        },
    ],
}


def build_settings() -> Settings:
    return Settings(
        api_base_url="https://api.example.com",
        api_key="test-key",
        api_email="user@example.com",
        api_password="secret",
        company_id="123",
        schedule_cron="0 6 * * *",
    )


def build_client(handler) -> httpx.Client:
    transport = httpx.MockTransport(handler)

    return httpx.Client(
        base_url="https://api.example.com",
        transport=transport,
    )


def build_token_manager(tokens=("token-1",)):
    token_manager = MagicMock()
    token_manager.get_token.side_effect = list(tokens) + ["token-N"] * 10
    return token_manager


class TestGetItemsHappyPath:
    def test_retorna_los_items_parseados(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.headers["Authorization"] == "Bearer token-1"
            assert request.url.params["idCompania"] == "123"

            return httpx.Response(200, json=VALID_ITEMS_PAYLOAD)

        settings = build_settings()
        client = build_client(handler)
        token_manager = build_token_manager()

        items_client = ItemsClient(
            settings=settings,
            client=client,
            token_manager=token_manager,
        )

        items = items_client.get_items()

        assert len(items) == 1
        assert items[0].item == 100
        assert items[0].descripcion_item == "Item de prueba"


class TestGetItemsRetryEn401:
    def test_renueva_token_y_reintenta_una_vez_tras_401(self):
        call_count = {"value": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            call_count["value"] += 1

            if call_count["value"] == 1:
                return httpx.Response(401, json={"message": "expired"})

            assert request.headers["Authorization"] == "Bearer token-2"

            return httpx.Response(200, json=VALID_ITEMS_PAYLOAD)

        settings = build_settings()
        client = build_client(handler)
        token_manager = build_token_manager(tokens=("token-1", "token-2"))

        items_client = ItemsClient(
            settings=settings,
            client=client,
            token_manager=token_manager,
        )

        items = items_client.get_items()

        assert call_count["value"] == 2
        assert len(items) == 1
        token_manager.invalidate.assert_called_once()

    def test_401_persistente_tras_reintento_lanza_unauthorized(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"message": "expired"})

        settings = build_settings()
        client = build_client(handler)
        token_manager = build_token_manager(tokens=("token-1", "token-2"))

        items_client = ItemsClient(
            settings=settings,
            client=client,
            token_manager=token_manager,
        )

        with pytest.raises(ExternalApiUnauthorizedError):
            items_client.get_items()


class TestGetItemsErroresHttp:
    @pytest.mark.parametrize(
        "status_code,expected_exception",
        [
            (403, ExternalApiForbiddenError),
            (404, ExternalApiNotFoundError),
            (429, ExternalApiRateLimitError),
            (500, ExternalApiServerError),
            (502, ExternalApiServerError),
            (503, ExternalApiServerError),
            (504, ExternalApiServerError),
            (418, ExternalApiError),
        ],
    )
    def test_status_code_se_mapea_a_la_excepcion_correcta(
        self,
        status_code,
        expected_exception,
    ):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code, json={"message": "error"})

        settings = build_settings()
        client = build_client(handler)
        token_manager = build_token_manager()

        items_client = ItemsClient(
            settings=settings,
            client=client,
            token_manager=token_manager,
        )

        with pytest.raises(expected_exception):
            items_client.get_items()


class TestGetItemsRespuestaInvalida:
    def test_respuesta_con_formato_inesperado_lanza_external_api_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"algo": "inesperado"})

        settings = build_settings()
        client = build_client(handler)
        token_manager = build_token_manager()

        items_client = ItemsClient(
            settings=settings,
            client=client,
            token_manager=token_manager,
        )

        with pytest.raises(ExternalApiError):
            items_client.get_items()
