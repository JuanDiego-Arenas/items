from pathlib import Path

import pytest
from pydantic import ValidationError

from report_items.config.settings import Settings


def build_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "api_base_url": "https://api.example.com",
        "api_key": "test-key",
        "api_email": "user@example.com",
        "api_password": "secret",
        "company_id": "123",
        "schedule_cron": "0 6 * * *",
    }
    values.update(overrides)

    return Settings(**values)


def test_resuelve_el_directorio_como_carpeta_hermana(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project_directory = tmp_path / "report-items"
    project_directory.mkdir()
    monkeypatch.chdir(project_directory)

    settings = build_settings(report_output_dir="Items")

    assert settings.resolved_report_output_dir == tmp_path / "Items"


def test_usa_la_ruta_interna_cuando_se_configura(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "container-reports"
    settings = build_settings(report_output_path=output_path)

    assert settings.resolved_report_output_dir == output_path


@pytest.mark.parametrize("directory_name", ["", ".", "..", "../Items", "foo/bar"])
def test_rechaza_rutas_como_nombre_de_carpeta(directory_name: str) -> None:
    with pytest.raises(ValidationError):
        build_settings(report_output_dir=directory_name)
