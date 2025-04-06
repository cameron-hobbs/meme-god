from django.core.management import BaseCommand

from src.reddit.models.sub import RedditSub
from src.scraper.reddit import RedditScraper


class Command(BaseCommand):
    def handle(self, *args, **options):
        RedditSub.objects.get_or_create(tag="memes")
        reddit_scraper = RedditScraper()
        reddit_scraper.scrape()
