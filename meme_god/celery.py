import os

from celery import Celery
from celery.schedules import crontab

app = Celery("meme_god", broker=os.environ.get("BROKER_URL", "redis://redis:6379/0"))

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "scrape_reddit": {
        "task": "src.reddit.tasks.scrape_posts",
        "schedule": crontab(minute="0", hour="9-21"),
    },
    "daily_suggestions": {
        "task": "src.media_sender.tasks.make_daily_suggestions",
        "schedule": crontab(hour=6, minute=0),
    },
}
