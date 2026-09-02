import os
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.cell import WriteOnlyCell
from openpyxl.styles import Font

from src.clients.items_client import Item
from src.reports.item_report_mapper import ItemReportMapper


class ExcelReportGenerator:
    def __init__(
        self,
        mapper: ItemReportMapper,
    ) -> None:
        self._mapper = mapper

    def generate(
        self,
        items: list[Item],
        output_directory: Path,
    ) -> Path:
        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = output_directory / "items.xlsx"

        temporary_path = output_directory / "items.tmp.xlsx"

        rows = self._mapper.map_items(items)

        workbook = Workbook(write_only=True)

        worksheet = workbook.create_sheet(
            title="Items",
        )

        headers = self._mapper.HEADERS

        worksheet.append(self._build_header_row(worksheet, headers))

        for row in rows:
            worksheet.append(
                [row.get(header, "") for header in headers],
            )

        workbook.save(temporary_path)

        os.replace(
            temporary_path,
            output_path,
        )

        return output_path

    @staticmethod
    def _build_header_row(
        worksheet: Any,
        headers: list[str],
    ) -> list[Any]:
        styled_headers = []

        for header in headers:
            cell = WriteOnlyCell(
                worksheet,
                value=header,
            )

            cell.font = Font(
                bold=True,
            )

            styled_headers.append(cell)

        return styled_headers
