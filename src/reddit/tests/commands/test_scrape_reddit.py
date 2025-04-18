from unittest.mock import patch

from django.core.management import call_command

from src.common.tests import BaseTest


class TestScrapeRedditCommand(BaseTest):
    def test_command(self) -> None:
        with patch("src.scraper.reddit.RedditScraper.scrape") as mock_scrape:
            call_command("scrape_reddit")
            mock_scrape.assert_called_once()
