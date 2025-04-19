__all__ = ["SuggestedMedia"]

from django.db import models

from src.common.choices import Topic, Source
from src.common.models import BaseCreatedAtModel


class SuggestedMedia(BaseCreatedAtModel):
    topic = models.CharField(max_length=255, choices=Topic.choices)
    source = models.CharField(max_length=255, choices=Source.choices)
    url = models.URLField(max_length=255)
    is_video = models.BooleanField(default=False)
    sent_to_telegram_at = models.DateTimeField(null=True)
    title = models.CharField(max_length=255)
