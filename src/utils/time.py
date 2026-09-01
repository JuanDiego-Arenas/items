from datetime import UTC, datetime


def build_api_timestamp() -> str:
    """Genera el timestamp ISO-8601 con milisegundos y sufijo 'Z'
    que exige la API externa.
    """
    return datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")
