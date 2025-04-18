import pytest

from src.reddit.models import RedditSub
from src.reddit.tests.factories import RedditSubFactory


class RedditModelTestMixin:
    pytestmark = [pytest.mark.django_db]

    @pytest.fixture
    def subreddits(self) -> list[RedditSub]:
        return RedditSubFactory.create_batch(5)
