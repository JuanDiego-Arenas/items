from unittest.mock import MagicMock

from src.auth.token_manager import TokenManager


def build_token_manager(login_return_values=None):
    auth_client = MagicMock()

    if login_return_values is not None:
        auth_client.login.side_effect = login_return_values

    return TokenManager(auth_client=auth_client), auth_client


class TestGetToken:
    def test_primera_llamada_hace_login_y_cachea_el_token(self):
        token_manager, auth_client = build_token_manager(["token-1"])

        token = token_manager.get_token()

        assert token == "token-1"
        auth_client.login.assert_called_once()

    def test_segunda_llamada_reutiliza_el_token_sin_volver_a_hacer_login(self):
        token_manager, auth_client = build_token_manager(["token-1"])

        first_token = token_manager.get_token()
        second_token = token_manager.get_token()

        assert first_token == second_token == "token-1"
        auth_client.login.assert_called_once()


class TestInvalidate:
    def test_invalidate_fuerza_un_nuevo_login_en_la_siguiente_llamada(self):
        token_manager, auth_client = build_token_manager(
            ["token-1", "token-2"],
        )

        first_token = token_manager.get_token()
        token_manager.invalidate()
        second_token = token_manager.get_token()

        assert first_token == "token-1"
        assert second_token == "token-2"
        assert auth_client.login.call_count == 2

    def test_invalidate_sin_token_previo_no_falla(self):
        token_manager, _auth_client = build_token_manager(["token-1"])

        token_manager.invalidate()
        token = token_manager.get_token()

        assert token == "token-1"
