from src.scraper.api_client.base import BaseApiClient


class RedditApiClient(BaseApiClient):
    def __init__(self):
        super().__init__("https://www.reddit.com")
