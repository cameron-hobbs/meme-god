__all__ = ["SuggestedMedia"]

from django.db import models

from src.common.choices import Topic, Source
from src.common.models import BaseCreatedAtModel


class SuggestedMedia(BaseCreatedAtModel):
    topic = models.CharField(max_length=255, choices=Topic.choices, null=True)
    source = models.CharField(max_length=255, choices=Source.choices, null=True)
    url = models.URLField(max_length=255)
    is_video = models.BooleanField(default=False)
