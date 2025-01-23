# fire_aprs_cli/scheduler.py

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import signal
import sys

class Scheduler:
    def __init__(self, interval_minutes, job_func, *args, **kwargs):
        self.scheduler = BackgroundScheduler()
        self.interval = interval_minutes
        self.job_func = job_func
        self.args = args
        self.kwargs = kwargs

    def start(self):
        trigger = IntervalTrigger(minutes=self.interval)
        self.scheduler.add_job(
            self.job_func,
            trigger,
            args=self.args,
            kwargs=self.kwargs,
            next_run_time=None,
            max_instances=1,
            coalesce=True,
            name="process_fire_data"
        )
        self.scheduler.start()
        logging.info(f"Scheduler started with interval: {self.interval} minutes.")

        # Handle graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        logging.info("Shutting down scheduler...")
        self.scheduler.shutdown()
        logging.info("Scheduler shut down successfully.")
        sys.exit(0)
