__all__ = ["RedditUser"]

from django.db import models

from src.common.models import BaseModel


class RedditUser(BaseModel):
    name = models.CharField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255, null=True)
