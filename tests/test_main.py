import pytest

from src.main import load_settings


def test_informa_las_variables_de_entorno_faltantes(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    monkeypatch.chdir(tmp_path)

    for variable in (
        "API_BASE_URL",
        "API_KEY",
        "API_EMAIL",
        "API_PASSWORD",
        "COMPANY_ID",
        "SCHEDULE_CRON",
    ):
        monkeypatch.delenv(variable, raising=False)

    with pytest.raises(SystemExit) as exc_info:
        load_settings()

    assert str(exc_info.value) == (
        "Faltan variables de entorno obligatorias: "
        "API_BASE_URL, API_KEY, API_EMAIL, API_PASSWORD, COMPANY_ID, "
        "SCHEDULE_CRON. Revise el archivo .env."
    )
