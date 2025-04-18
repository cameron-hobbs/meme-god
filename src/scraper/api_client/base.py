import logging
from typing import Any

import requests
from requests import Response, HTTPError

logger = logging.getLogger(__name__)


class BaseApiClient:
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
    }

    def __init__(self, base_url: str):
        self._base_url = base_url

    def request(self, endpoint: str, **kwargs: Any) -> Response | None:
        headers = self.default_headers
        if (custom_headers := kwargs.get("headers")) is not None:
            user_agent = custom_headers.get("User-Agent", headers["User-Agent"])
            headers = custom_headers
            headers["User-Agent"] = user_agent

        response = requests.get(f"{self._base_url}/{endpoint}", headers=headers)
        try:
            response.raise_for_status()
        except HTTPError as e:
            logger.warning("There was an error with an api request")
            logger.error(e, exc_info=True)
            return None

        logger.info("Got data successfully")
        return response

    def json_request(self, endpoint: str, **kwargs: Any) -> dict | None:
        response = self.request(endpoint, **kwargs)
        if response is None:
            return response
        return response.json()
