import httpx
import pytest

from report_items.clients.auth_client import AuthClient
from report_items.config.settings import Settings
from report_items.exceptions.external_api import ExternalApiAuthError


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


class TestLoginExitoso:
    def test_retorna_el_token_de_autorizacion(self):
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/auth/login"
            assert request.headers["x-api-key"] == "test-key"

            return httpx.Response(
                200,
                json={
                    "message": "ok",
                    "authorization": "Bearer abc123",
                },
            )

        settings = build_settings()
        client = build_client(handler)
        auth_client = AuthClient(settings=settings, client=client)

        token = auth_client.login()

        assert token == "Bearer abc123"

    def test_envia_email_y_password_en_el_body(self):
        import json

        captured_body = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured_body.update(json.loads(request.content))

            return httpx.Response(
                200,
                json={"message": "ok", "authorization": "token"},
            )

        settings = build_settings()
        client = build_client(handler)
        auth_client = AuthClient(settings=settings, client=client)

        auth_client.login()

        assert captured_body["email"] == "user@example.com"
        assert captured_body["password"] == "secret"


class TestLoginConError:
    def test_http_error_lanza_external_api_auth_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"message": "unauthorized"})

        settings = build_settings()
        client = build_client(handler)
        auth_client = AuthClient(settings=settings, client=client)

        with pytest.raises(ExternalApiAuthError):
            auth_client.login()

    def test_respuesta_con_formato_invalido_lanza_external_api_auth_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"algo": "inesperado"})

        settings = build_settings()
        client = build_client(handler)
        auth_client = AuthClient(settings=settings, client=client)

        with pytest.raises(ExternalApiAuthError):
            auth_client.login()
