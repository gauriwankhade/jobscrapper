# jobs/management/commands/run_scheduler.py
import signal
import sys
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from jobs.scraper import scrape_remoteok as scrape_jobs_task  # import your scraper function
from django.utils import timezone   # <-- add this


from jobs.scheduler_jobs import hello_job  # demo
# we'll add the real scraper in Part B

class Command(BaseCommand):
    help = "Starts APScheduler with Django job store (cross-platform)."

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")


        scheduler.add_job(
            scrape_jobs_task,
            trigger=CronTrigger(minute="*/2"),   # every minute for testing
            kwargs={"limit": 20},
            id="scrape_every_minute",
            max_instances=1,
            coalesce=True,
            replace_existing=True,
            misfire_grace_time=60,
            jobstore="default",
            next_run_time=timezone.now(),        # run once right now so you see output
        )


        register_events(scheduler)
        scheduler.start()
        self.stdout.write(self.style.SUCCESS("✓ APScheduler started."))

        # graceful shutdown
        def shutdown(signum, frame):
            self.stdout.write("Shutting down scheduler…")
            scheduler.shutdown(wait=False)
            sys.exit(0)

        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, shutdown)

        # Keep process alive
        try:
            signal.pause()
        except AttributeError:
            # Windows Python lacks signal.pause(); use a simple loop
            import time
            while True:
                time.sleep(1)
