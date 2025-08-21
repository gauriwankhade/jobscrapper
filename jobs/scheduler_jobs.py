# jobs/scheduler_jobs.py
from django.utils import timezone

def hello_job():
    # Keep it obvious in dev; replace with logging in prod
    print("APScheduler says hello at", timezone.now().isoformat())
