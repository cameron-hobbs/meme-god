import logging

from meme_god.celery import app
from src.common.lock import acquire_lock
from src.media_sender.send_media import send_media
from src.media_sender.suggestion.engine import SuggestionEngine
from src.media_sender.telegram_bot import TelegramBotError
from src.reddit.models import RankedRedditPost

logger = logging.getLogger(__name__)


@app.task(bind=True, acks_late=True)
def make_daily_suggestions(self) -> None:
    if not acquire_lock("daily-suggestions", timeout=60):
        self.retry(countdown=60)
        logger.debug("Could not acquire lock for daily suggestions, retrying in 60s")
        return

    RankedRedditPost.refresh()
    suggestion_engine = SuggestionEngine()
    suggestion_engine.run()


@app.task(
    bind=True, acks_late=True, max_retries=None, soft_time_limit=30, time_limit=60
)
def fetch_media_and_send_to_telegram(self, suggested_media_id: int) -> None:
    if not acquire_lock("telegram-msg", timeout=3):
        self.retry(countdown=1)
        logger.debug("Could not acquire lock for telegram msg, retrying in 1s")
        return

    try:
        send_media(suggested_media_id)
    except TelegramBotError:
        retry_delay = 2**self.request.retries
        logger.debug(f"Retrying in {retry_delay}s")
        self.retry(countdown=retry_delay)
