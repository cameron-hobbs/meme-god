__all__ = ["RedditSub"]

from django.db import models

from src.common.choices import Topic
from src.common.models import BaseModel


class RedditSub(BaseModel):
    tag = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255, choices=Topic.choices)
    should_scrape = models.BooleanField(default=True)
    subscribers = models.IntegerField(null=True)
