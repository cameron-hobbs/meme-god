import logging

from meme_god.celery import app
from src.common.lock import acquire_lock
from src.scraper.reddit import RedditScraper

logger = logging.getLogger(__name__)


@app.task(bind=True)
def scrape_posts(self) -> None:
    if not acquire_lock("scrape-reddit-posts", timeout=360):
        logger.debug("Could not acquire lock for scrape posts, retrying in 360s")
        self.retry(countdown=360)
        return
    reddit_scraper = RedditScraper()
    reddit_scraper.scrape()
