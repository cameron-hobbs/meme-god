import random
from unittest.mock import patch

import pytest

from src.common.tests import BaseTest
from src.reddit.models import RedditPostChangeLog, RedditPost, RedditSub, RedditUser
from src.reddit.tests.mixin import RedditModelTestMixin
from src.scraper.reddit import RedditScraper
from src.scraper.tests.mixins import RedditAPIDataTestMixin


class TestRedditScraper(BaseTest, RedditModelTestMixin, RedditAPIDataTestMixin):
    @pytest.fixture(scope="class", autouse=True)
    def scraper(self) -> RedditScraper:
        return RedditScraper()

    def test_scraper_model_types(self, scraper: RedditScraper) -> None:
        assert scraper.change_log_model is RedditPostChangeLog
        assert scraper.comparison_model is RedditPost

    @pytest.fixture
    def expected_ignore_change_fields(self) -> set[str]:
        return {"change_log", "id", "created_at", "updated_at", "subreddit_subscribers"}

    def test_ignore_change_fields(
        self, scraper: RedditScraper, expected_ignore_change_fields: set[str]
    ) -> None:
        assert scraper.ignore_change_fields() == expected_ignore_change_fields

    @pytest.mark.parametrize(
        ["field", "old_value", "new_value", "expected_cancelled"],
        [
            pytest.param(
                "upvote_ratio", "0.9", "0.90", True, id="upvote_ratio_same_diff_types"
            ),
            pytest.param(
                "upvote_ratio", "0.9", "0.92", False, id="upvote_ratio_changed"
            ),
        ],
        # todo: all available fields for the model type
    )
    def test_cancel_comparison(
        self,
        scraper: RedditScraper,
        field: str,
        old_value: str,
        new_value: str,
        expected_cancelled: bool,
    ) -> None:
        assert (
            scraper.cancel_comparison(field, old_value, new_value) == expected_cancelled
        )

    def test_compare_changes(self, scraper: RedditScraper) -> None:
        pytest.fail("not implemented yet")

    def test_scrape(self, scraper: RedditScraper, subreddits: list[RedditSub]) -> None:
        with patch.object(scraper, "_scrape_category") as mock:
            scraper.scrape()
            assert mock.call_count == 20
            # todo: test a bit more here for call args

    @pytest.fixture
    def select_category(self) -> str:
        return random.choice(["best", "new", "hot", "rising"])

    def test_scrape_category(
        self,
        scraper: RedditScraper,
        subreddits: list[RedditSub],
        reddit_category_data: dict,
        select_category: str,
        requests_mock,
        reddit_post: dict,
        other_reddit_post: dict,
    ) -> None:
        select_subreddit = random.choice(subreddits)
        mock_url = (
            f"https://www.reddit.com/r/{select_subreddit.tag}/{select_category}/.json"
        )
        requests_mock.get(mock_url, json=reddit_category_data)

        with patch.object(scraper, "_process_post") as mock:
            scraper._scrape_category(select_subreddit, select_category)
            assert mock.call_count == 2
            first_call_args = mock.call_args_list[0].args
            second_call_args = mock.call_args_list[1].args
            assert all(
                called_subreddit == select_subreddit
                for called_subreddit in {first_call_args[0], second_call_args[0]}
            )
            assert first_call_args[1] == reddit_post
            assert second_call_args[1] == other_reddit_post

    def test_process_post_new(
        self, scraper: RedditScraper, subreddits: list[RedditSub], reddit_post: dict
    ) -> None:
        select_subreddit = random.choice(subreddits)

        scraper._process_post(select_subreddit, reddit_post.copy())

        expected_author_id = RedditUser.objects.get(name="cameron-hobbs").id
        actual = RedditPost.objects.get()
        assert actual.author_id == expected_author_id
        assert actual.subreddit_id == select_subreddit.id
        assert actual.post_id == reddit_post["id"]
        # todo: check all data created

    def test_process_post_existing(
        self, scraper: RedditScraper, subreddits: list[RedditSub], reddit_post: dict
    ) -> None:
        pytest.fail("not implemented yet")
