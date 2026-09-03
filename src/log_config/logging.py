import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo


class _TimezoneFormatter(logging.Formatter):
    def __init__(self, *args: object, tz: ZoneInfo, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self._tz = tz

    def formatTime(
        self,
        record: logging.LogRecord,
        datefmt: str | None = None,
    ) -> str:
        moment = datetime.fromtimestamp(record.created, tz=self._tz)

        if datefmt:
            return moment.strftime(datefmt)

        return moment.isoformat(timespec="milliseconds")


def configure_logging(timezone: str) -> None:
    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(
        _TimezoneFormatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            "%Y-%m-%d %H:%M:%S",
            tz=ZoneInfo(timezone),
        )
    )

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )
