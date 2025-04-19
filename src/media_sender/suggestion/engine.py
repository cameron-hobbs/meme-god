import logging
from dataclasses import dataclass
from collections import defaultdict
from datetime import timedelta

from django.utils import timezone

from src.common.choices import Topic
from src.media_sender.models import SuggestedMedia
from src.media_sender.suggestion.processor import (
    SuggestionProcessor,
    RankedSuggestedMedia,
)

logger = logging.getLogger(__name__)

MAX_VIDEOS_PER_TOPIC = 3
MAX_IMAGES_PER_TOPIC = 10


@dataclass
class SelectedSuggestions:
    topic: Topic
    images: list[SuggestedMedia]
    videos: list[SuggestedMedia]


class SuggestionEngine:
    def __init__(self) -> None:
        self.processor = SuggestionProcessor()

    def run(self) -> None:
        logger.info("Generating suggestions...")

        ranked = self.processor.get_fresh_suggestions()
        grouped = self._group_by_topic(ranked)

        for topic, ranked_suggestions in grouped.items():
            images, videos = self._select_top_suggestions(ranked_suggestions)
            logger.info(
                "Selected %s images and %s videos for topic '%s'",
                len(images),
                len(videos),
                topic,
            )

            suggestions = SelectedSuggestions(topic=topic, images=images, videos=videos)
            suggested_medias = suggestions.images + suggestions.videos
            SuggestedMedia.objects.bulk_create(suggested_medias)

            created_suggestions = SuggestedMedia.objects.filter(
                url__in=[suggested_media.url for suggested_media in suggested_medias],
                created_at__gte=timezone.now() - timedelta(seconds=30),
            )

            logger.info(
                "Got %s created suggestions triggering tasks for",
                created_suggestions.count(),
            )
            for created_suggestion in created_suggestions:
                from src.media_sender.tasks import fetch_media_and_send_to_telegram

                fetch_media_and_send_to_telegram.delay(created_suggestion.id)

    @staticmethod
    def _group_by_topic(
        ranked_suggestions: list[RankedSuggestedMedia],
    ) -> dict[Topic, list[RankedSuggestedMedia]]:
        grouped = defaultdict(list)
        for item in ranked_suggestions:
            grouped[item.suggestion.topic].append(item)
        return grouped

    @staticmethod
    def _select_top_suggestions(
        ranked: list[RankedSuggestedMedia],
    ) -> tuple[list[SuggestedMedia], list[SuggestedMedia]]:
        sorted_ranked = sorted(ranked, key=lambda x: x.ranking, reverse=True)

        images: list[SuggestedMedia] = []
        videos: list[SuggestedMedia] = []

        for suggestion in (s.suggestion for s in sorted_ranked):
            if suggestion.is_video and len(videos) < MAX_VIDEOS_PER_TOPIC:
                videos.append(suggestion)
            elif not suggestion.is_video and len(images) < MAX_IMAGES_PER_TOPIC:
                images.append(suggestion)
            if (
                len(videos) >= MAX_VIDEOS_PER_TOPIC
                and len(images) >= MAX_IMAGES_PER_TOPIC
            ):
                break

        return images, videos
