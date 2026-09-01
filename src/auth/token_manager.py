from report_items.clients.auth_client import AuthClient


class TokenManager:
    def __init__(self, auth_client: AuthClient) -> None:
        self._auth_client = auth_client
        self._token: str | None = None

    def get_token(self) -> str | None:
        if self._token is None:
            self._token = self._auth_client.login()

        return self._token

    def invalidate(self) -> None:
        self._token = None
