import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta, date
from itertools import chain
from typing import TypeVar, Generic

from django.db.models import QuerySet

from src.common.choices import Source
from src.common.models import BaseRankedPost
from src.media_sender.models import SuggestedMedia
from src.reddit.models import RankedRedditPost


logger = logging.getLogger(__name__)
_MAPPED_SOURCE_RANKED_MODELS: dict[Source, type[BaseRankedPost]] = {
    Source.REDDIT: RankedRedditPost
}


@dataclass
class KeptPostMetric:
    before_count: int
    after_count: int


@dataclass
class Metrics:
    kept_post: KeptPostMetric = None

    def __str__(self):
        return f"Kept {self.kept_post.after_count} (out of {self.kept_post.before_count}) posts."


@dataclass
class RankedSuggestedMedia:
    suggestion: SuggestedMedia
    ranking: int


T = TypeVar("T", bound=BaseRankedPost)


class BaseSuggestionHandler(ABC, Generic[T]):
    @abstractmethod
    def handle_suggestions(
        self, ranked_posts: QuerySet[T], recent_suggestion_urls: set[str]
    ) -> list[RankedSuggestedMedia]:
        raise NotImplementedError


class RedditSuggestionHandler(BaseSuggestionHandler[RankedRedditPost]):
    def handle_suggestions(
        self, ranked_posts: QuerySet[T], recent_suggestion_urls: set[str]
    ) -> list[RankedSuggestedMedia]:
        unseen_posts = ranked_posts.exclude(
            reddit_post__url__in=recent_suggestion_urls
        ).seal()
        return [
            RankedSuggestedMedia(
                suggestion=SuggestedMedia(
                    source=Source.REDDIT,
                    topic=unseen_post.reddit_post.subreddit.category,
                    url=unseen_post.reddit_post.url,
                    is_video=unseen_post.reddit_post.is_video,
                ),
                ranking=unseen_post.ranking,
            )
            for unseen_post in unseen_posts
        ]


class SuggestionProcessor:
    def __init__(self) -> None:
        self.source_ranked_posts: dict[Source, QuerySet] = {
            source: model_cls.objects.filter(
                created_at__date__gte=date.today() - timedelta(days=1)
            )
            for source, model_cls in _MAPPED_SOURCE_RANKED_MODELS.items()
        }
        self.suggestion_handler_map: dict[Source, BaseSuggestionHandler] = {
            Source.REDDIT: RedditSuggestionHandler()
        }
        self.suggestions: dict[Source, list[RankedSuggestedMedia]] = {}
        self.metrics: dict[Source, Metrics] = {}

    def get_fresh_suggestions(self) -> list[RankedSuggestedMedia]:
        if len(self.suggestions) > 0:
            logger.info("Already made suggestions, not getting new ones.")
            return []

        logger.info("Getting fresh suggestions")

        recent_suggestion_urls = set(
            SuggestedMedia.objects.filter(
                created_at__date__gte=date.today() - timedelta(days=30)
            ).values_list("url", flat=True)
        )
        logger.debug("Recent suggestion urls are %s", recent_suggestion_urls)

        for source, ranked_posts in self.source_ranked_posts.items():
            logger.info("Processing ranked posts for %s", source)
            logger.debug("Ranked posts pre-processing are: %s", ranked_posts)

            ranked_posts_count = ranked_posts.count()
            suggestion_handler = self.suggestion_handler_map[source]
            suggestions = suggestion_handler.handle_suggestions(
                ranked_posts, recent_suggestion_urls
            )
            logger.debug("Ranked posts post-processing are: %s", suggestions)
            num_suggestions = len(suggestions)

            self.suggestions[source] = suggestions
            metrics = Metrics(
                kept_post=KeptPostMetric(
                    before_count=ranked_posts_count, after_count=num_suggestions
                )
            )
            self.metrics[source] = metrics

            logger.info("Processed ranked posts for %s", source)
            logger.info("Metrics are: %s", metrics)

        return list(chain.from_iterable(self.suggestions.values()))
