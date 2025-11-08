from zoneinfo import ZoneInfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.scheduler.jobs import register_jobs


TZ = ZoneInfo("America/Santiago")
scheduler = AsyncIOScheduler(timezone=TZ)


def start_scheduler() -> None:
    try:
        register_jobs(scheduler)
        scheduler.start()
    except Exception as e:
        pass


def stop_scheduler() -> None:
    try:
        scheduler.shutdown(wait=False)
    except Exception as e:
        pass
