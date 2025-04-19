__all__ = ["Topic", "Source"]

from django.db import models


class Topic(models.TextChoices):
    MEMES = "memes"
    LONDON = "london"
    FOOD = "food"
    ANIMALS = "animals"
    CHINA = "china"


class Source(models.TextChoices):
    REDDIT = "reddit"
