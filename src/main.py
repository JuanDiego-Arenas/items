import httpx

from report_items.auth.token_manager import TokenManager
from report_items.clients.auth_client import AuthClient
from report_items.clients.items_client import ItemsClient
from report_items.config.settings import Settings
from report_items.jobs.report_job import ReportJob
from report_items.logging.logger import configure_logging
from report_items.reports.excel_report import ExcelReportGenerator
from report_items.reports.item_report_mapper import ItemReportMapper
from report_items.scheduler.scheduler import ReportScheduler


def main() -> None:
    configure_logging()

    settings = Settings()

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
