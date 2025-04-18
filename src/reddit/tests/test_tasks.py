from unittest.mock import patch

from src.common.tests import BaseTest
from src.reddit.tasks import scrape_posts


class TestRedditTasks(BaseTest):
    def test_scrape_posts_task(self) -> None:
        with patch("src.scraper.reddit.RedditScraper.scrape") as mock_scrape:
            scrape_posts()
            mock_scrape.assert_called_once()
