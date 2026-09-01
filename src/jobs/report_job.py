import logging

from report_items.clients.items_client import ItemsClient
from report_items.config.settings import Settings
from report_items.exceptions.external_api import ExternalApiError
from report_items.reports.excel_report import ExcelReportGenerator

logger = logging.getLogger(__name__)


class ReportJob:
    def __init__(
        self,
        items_client: ItemsClient,
        report_generator: ExcelReportGenerator,
        settings: Settings,
    ) -> None:
        self._items_client = items_client
        self._report_generator = report_generator
        self._settings = settings

    def run(self) -> None:
        logger.info(
            "Iniciando generación del reporte",
        )

        try:
            items = self._items_client.get_items()

            logger.info(
                "Generando archivo Excel con %s items",
                len(items),
            )

            output_path = self._report_generator.generate(
                items=items,
                output_directory=self._settings.resolved_report_output_dir,
            )

            logger.info(
                "Reporte generado correctamente: %s",
                output_path,
            )
        except ExternalApiError:
            logger.exception(
                "La ejecución del reporte falló",
            )
