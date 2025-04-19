__all__ = ["TopicChannel"]

from django.db import models

from src.common.choices import Topic
from src.common.models import BaseCreatedAtModel


class TopicChannel(BaseCreatedAtModel):
    topic = models.CharField(max_length=255, choices=Topic.choices)
    channel = models.CharField(max_length=100)
