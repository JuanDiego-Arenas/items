from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_base_url: str

    api_key: str
    api_email: str
    api_password: str

    api_channel: str = "API"
    api_timeout: float = 60.0

    company_id: str

    schedule_cron: str
    schedule_timezone: str = "America/Bogota"

    report_output_dir: str = "Items"
    report_output_path: Path | None = None

    @field_validator("report_output_dir")
    @classmethod
    def validate_report_output_dir(cls, value: str) -> str:
        directory_name = value.strip()

        if (
            not directory_name
            or directory_name in {".", ".."}
            or "/" in directory_name
            or "\\" in directory_name
        ):
            raise ValueError(
                "REPORT_OUTPUT_DIR debe ser solo el nombre de una carpeta."
            )

        return directory_name

    @property
    def resolved_report_output_dir(self) -> Path:
        if self.report_output_path is not None:
            return self.report_output_path

        return Path.cwd().parent / self.report_output_dir

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
