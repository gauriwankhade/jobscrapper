# jobs/tasks.py
import os, time
from django.utils import timezone
from .scraper import scrape_remoteok

# Simple cross-platform file lock to prevent overlapping runs
def _lock_path():
    return r"C:\Windows\Temp\scrape_jobs.lock" if os.name == "nt" else "/tmp/scrape_jobs.lock"

class FileLock:
    def __init__(self, path, timeout=1.5):
        self.path = path
        self.timeout = timeout
        self.fd = None
    def __enter__(self):
        start = time.time()
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                return self
            except FileExistsError:
                if time.time() - start > self.timeout:
                    raise TimeoutError("lock busy")
                time.sleep(0.2)
    def __exit__(self, exc_type, exc, tb):
        if self.fd is not None:
            os.close(self.fd)
            try:
                os.remove(self.path)
            except FileNotFoundError:
                pass

def scrape_jobs_task(limit=20):
    """
    Call your existing scraper and return a short status string.
    Idempotency is already handled via update_or_create in your code.
    """
    lockfile = _lock_path()
    try:
        with FileLock(lockfile):
            started = timezone.now()
            scrape_remoteok(limit=limit)
            return f"Scrape OK {started.isoformat()} → {timezone.now().isoformat()}"
    except TimeoutError:
        return "Skipped (another scrape in progress)"
