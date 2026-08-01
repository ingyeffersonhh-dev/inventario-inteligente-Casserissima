from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

jobstores = {
    'default': SQLAlchemyJobStore(url=settings.db_path_sync, tablename='apscheduler_jobs')
}

scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="America/Caracas")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler iniciado")
