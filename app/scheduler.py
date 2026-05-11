import sys
import io

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import pytz
import logging

from core.logger import setup_logger
from core.orchestrator import NeuraCore

logger = setup_logger()
IST = pytz.timezone("Asia/Kolkata")


def run_daily_pipeline():
    logger.info(
        f"Pipeline triggered at "
        f"{datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')} IST"
    )
    try:
        core = NeuraCore()
        core.run()
        logger.info("Daily pipeline completed!")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")


# Run once on startup
logger.info("Running pipeline on startup...")
run_daily_pipeline()

# Schedule daily at 7:00 AM IST
scheduler = BlockingScheduler(timezone=IST)
scheduler.add_job(
    run_daily_pipeline,
    CronTrigger(hour=7, minute=0, timezone=IST),
    id="daily_neuraflow",
    name="NeuraFlow Daily Pipeline"
)

logger.info("Scheduler started! Runs every day at 7:00 AM IST")

try:
    scheduler.start()
except KeyboardInterrupt:
    logger.info("Scheduler stopped!")