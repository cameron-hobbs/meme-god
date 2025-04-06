__all__ = ["RedditUser"]

from django.db import models

from src.common.models import BaseModel


class RedditUser(BaseModel):
    full_name = models.CharField(unique=True, max_length=255)
