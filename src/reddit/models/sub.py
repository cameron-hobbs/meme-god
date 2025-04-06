__all__ = ["RedditSub"]

from django.db import models

from src.common.models import BaseModel


class SubCategory(models.TextChoices):
    MEMES = "memes"
    LONDON = "london"
    FOOD = "food"
    ANIMALS = "animals"
    CHINA = "china"


class RedditSub(BaseModel):
    tag = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=255, choices=SubCategory.choices, null=True)
    should_scrape = models.BooleanField(default=True)
    subscribers = models.IntegerField(null=True)
