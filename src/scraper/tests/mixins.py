from uuid import uuid4

import pytest
import time


class RedditAPIDataTestMixin:
    @pytest.fixture
    def reddit_post(self) -> dict:
        return {
            "author_fullname": "cameron-hobbs",
            "id": uuid4().hex,
            "created_utc": int(time.time()),
            "over_18": False,
            "send_replies": True,
            "is_video": False,
            "score": 95,
            "ups": 100,
            "downs": 5,
            "upvote_ratio": 0.95,
            "total_awards_received": 1,
            "is_created_from_ads_ui": False,
            "edited": False,
            "pinned": False,
            "num_comments": 25,
            "is_self": False,
            "quarantine": False,
        }

    @pytest.fixture
    def other_reddit_post(self) -> dict:
        # todo: gen data
        return {}

    @pytest.fixture
    def reddit_category_data(self, reddit_post: dict, other_reddit_post: dict) -> dict:
        return {
            "data": {"children": [{"data": reddit_post}, {"data": other_reddit_post}]}
        }
