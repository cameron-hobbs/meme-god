from meme_god.celery import app
from src.scraper.reddit import RedditScraper


@app.task
def scrape_posts() -> None:
    reddit_scraper = RedditScraper()
    reddit_scraper.scrape()
