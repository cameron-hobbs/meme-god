from celery import Celery
from celery.schedules import crontab

app = Celery("meme_god", broker="redis://redis:6379/0")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "scrape_reddit": {
        "task": "src.reddit.tasks.scrape_posts",
        "schedule": crontab(minute="*/5"),
    },
}
