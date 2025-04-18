__all__ = ["RankedRedditPost"]

from dataclasses import dataclass
from datetime import date, timedelta

from django.db import models
from django.db.models import (
    Q,
    F,
    ExpressionWrapper,
    DurationField,
    FloatField,
    Max,
    QuerySet,
)
from django.db.models.functions import Now, Extract

from src.common.models import BaseModel
from src.reddit.models import RedditPost


@dataclass
class FilteredPostsMax:
    max_score: float
    max_comments: float
    max_age: float


class RankedRedditPost(BaseModel):
    ranking = models.FloatField(default=0)
    reddit_post = models.ForeignKey(RedditPost, on_delete=models.CASCADE, unique=True)

    @staticmethod
    def get_filtered_posts() -> QuerySet[RedditPost]:
        q = Q()

        for url_match in {"i.redd.it", "v.redd.it", "gallery", "png", "jpeg"}:
            q |= Q(url__contains=url_match)

        q |= Q(is_video=True)

        return (
            RedditPost.objects.filter(q)
            .filter(post_created_at__date=date.today(), over_18=False)
            .alias(
                minutes_since_created=ExpressionWrapper(
                    (Now() - F("post_created_at")), output_field=DurationField()
                ),
            )
            .annotate(
                minutes_since_created_float=ExpressionWrapper(
                    Extract(F("minutes_since_created"), "epoch") / 60.0,
                    output_field=FloatField(),
                )
            )
        )

    @staticmethod
    def get_filtered_post_aggregate_max(
        filtered_posts: QuerySet[RedditPost],
    ) -> FilteredPostsMax:
        agg = filtered_posts.aggregate(
            max_score=Max("score"),
            max_comments=Max("num_comments"),
            max_age=Max("minutes_since_created_float"),
        )

        max_score = agg["max_score"] or 1
        max_comments = agg["max_comments"] or 1
        max_age = agg["max_age"] or 1

        return FilteredPostsMax(
            max_score=float(max_score),
            max_comments=float(max_comments),
            max_age=float(max_age),
        )

    @classmethod
    def refresh(cls) -> None:
        cls.objects.filter(
            created_at__date__lte=date.today() - timedelta(days=2)
        ).delete()
        filtered_posts = cls.get_filtered_posts()
        filtered_posts_max = cls.get_filtered_post_aggregate_max(filtered_posts)

        queryset = (
            filtered_posts.annotate(
                normalized_score=F("score") / filtered_posts_max.max_score,
                normalized_comments=F("num_comments") / filtered_posts_max.max_comments,
                normalized_upvote_ratio=F("upvote_ratio"),
                normalized_age=(
                    1 - (F("minutes_since_created_float") / filtered_posts_max.max_age)
                ),
            )
            .annotate(
                ranking=ExpressionWrapper(
                    F("normalized_score") + F("normalized_comments"),
                    # 0.1 * F("normalized_upvote_ratio") +
                    # 0.1 * F("normalized_age"),
                    output_field=FloatField(),
                )
            )
            .values("id", "ranking")
        )

        current_post_ids = set()
        to_update = []
        to_create = []

        existing_ranked = {
            r.reddit_post_id: r
            for r in RankedRedditPost.objects.filter(
                reddit_post_id__in=[obj["id"] for obj in queryset]
            )
        }

        for obj in queryset:
            reddit_post_id = obj["id"]
            current_post_ids.add(reddit_post_id)
            ranking = obj["ranking"]

            if reddit_post_id in existing_ranked:
                ranked_post = existing_ranked[reddit_post_id]
                ranked_post.ranking = ranking
                to_update.append(ranked_post)
            else:
                to_create.append(
                    RankedRedditPost(reddit_post_id=reddit_post_id, ranking=ranking)
                )

        if to_update:
            RankedRedditPost.objects.bulk_update(to_update, ["ranking"])
        if to_create:
            RankedRedditPost.objects.bulk_create(to_create)
