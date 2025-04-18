__all__ = ["RedditPost", "RedditPostChangeLog"]

from django.db import models

from src.common.models import BaseModel, BaseChangeLog
from src.reddit.models.sub import RedditSub
from src.reddit.models.user import RedditUser


class RedditPost(BaseModel):
    author = models.ForeignKey(
        RedditUser, on_delete=models.PROTECT, related_name="content_posted"
    )
    subreddit = models.ForeignKey(
        RedditSub, on_delete=models.PROTECT, related_name="posts"
    )
    title = models.CharField(max_length=255)
    over_18 = models.BooleanField()
    post_id = models.CharField(max_length=255, unique=True)
    send_replies = models.BooleanField()
    is_video = models.BooleanField()
    post_created_at = models.DateTimeField()
    score = models.IntegerField()
    ups = models.IntegerField()
    downs = models.IntegerField()
    pwls = models.IntegerField(null=True)
    upvote_ratio = models.DecimalField(decimal_places=2, max_digits=3)
    total_awards_received = models.IntegerField()
    is_created_from_ads_ui = models.BooleanField()
    edited = models.BooleanField(null=True)  # null if it was a float -- ignored
    post_hint = models.CharField(max_length=255)
    pinned = models.BooleanField()
    url = models.URLField(max_length=255)
    num_comments = models.IntegerField()
    is_self = models.BooleanField()
    num_reports = models.IntegerField(null=True)
    thumbnail_height = models.IntegerField(null=True)
    thumbnail_width = models.IntegerField(null=True)
    quarantine = models.BooleanField()


class RedditPostChangeLog(BaseChangeLog):
    post = models.ForeignKey(
        RedditPost, on_delete=models.CASCADE, related_name="change_log"
    )
