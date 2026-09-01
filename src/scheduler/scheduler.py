import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from report_items.config.settings import Settings
from report_items.jobs.report_job import ReportJob

logger = logging.getLogger(__name__)


class ReportScheduler:
    def __init__(
        self,
        settings: Settings,
        job: ReportJob,
    ) -> None:
        self._settings = settings
        self._job = job

    def run(self) -> None:
        scheduler = BlockingScheduler(
            timezone=self._settings.schedule_timezone,
        )

        trigger = CronTrigger.from_crontab(
            self._settings.schedule_cron,
            timezone=self._settings.schedule_timezone,
        )

        scheduler.add_job(
            self._job.run,
            trigger=trigger,
            id="generate_items_report",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
        )

        logger.info(
            "Scheduler iniciado. Cron: %s",
            self._settings.schedule_cron,
        )

        logger.info(
            "Zona horaria del scheduler: %s",
            self._settings.schedule_timezone,
        )

        try:
            scheduler.start()

        except KeyboardInterrupt, SystemExit:
            logger.info("Scheduler detenido")
