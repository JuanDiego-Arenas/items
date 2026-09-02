import httpx
from pydantic import ValidationError

from src.auth.token_manager import TokenManager
from src.clients.auth_client import AuthClient
from src.clients.items_client import ItemsClient
from src.config.settings import Settings
from src.jobs.report_job import ReportJob
from src.logging.logger import configure_logging
from src.reports.excel_report import ExcelReportGenerator
from src.reports.item_report_mapper import ItemReportMapper
from src.scheduler.scheduler import ReportScheduler


def load_settings() -> Settings:
    try:
        return Settings()  # pyright: ignore[reportCallIssue]
    except ValidationError as exc:
        missing_variables = [
            str(error["loc"][0]).upper()
            for error in exc.errors()
            if error["type"] == "missing"
        ]

        if missing_variables:
            variables = ", ".join(missing_variables)
            raise SystemExit(
                f"Faltan variables de entorno obligatorias: {variables}. "
                "Revise el archivo .env."
            ) from exc

        raise SystemExit("El archivo .env contiene valores inválidos.") from exc


def main() -> None:
    configure_logging()

    settings = load_settings()

    with httpx.Client(
        base_url=settings.api_base_url,
        timeout=settings.api_timeout,
    ) as http_client:
        auth_client = AuthClient(
            settings=settings,
            client=http_client,
        )

        token_manager = TokenManager(
            auth_client=auth_client,
        )

        items_client = ItemsClient(
            settings=settings,
            client=http_client,
            token_manager=token_manager,
        )

        item_report_mapper = ItemReportMapper()

        report_generator = ExcelReportGenerator(
            mapper=item_report_mapper,
        )

        job = ReportJob(
            items_client=items_client,
            report_generator=report_generator,
            settings=settings,
        )

        scheduler = ReportScheduler(
            settings=settings,
            job=job,
        )

        scheduler.run()


if __name__ == "__main__":
    main()
