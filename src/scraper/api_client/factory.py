from typing import TypeVar

from src.scraper.api_client.base import BaseApiClient
from src.scraper.api_client.reddit import RedditApiClient

_API_CLIENTS = {"reddit": RedditApiClient()}


T = TypeVar("T", bound=BaseApiClient)


def get_api_client(site: str) -> T:
    return _API_CLIENTS[site]
