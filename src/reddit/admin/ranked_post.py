from django.contrib import admin
from django.utils.html import format_html
from datetime import date

from src.reddit.models import RankedRedditPost


@admin.register(RankedRedditPost)
class RankedRedditPostAdmin(admin.ModelAdmin):
    list_display = (
        "subreddit_category",
        "post_url",
        "reddit_post__title",
        "ranking",
        "reddit_post__score",
        "reddit_post__num_comments",
        "reddit_post__upvote_ratio",
    )
    list_filter = ("reddit_post__subreddit__category",)

    def subreddit_category(self, obj):
        return obj.reddit_post.subreddit.category or obj.reddit_post.subreddit.tag

    def post_url(self, obj):
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            obj.reddit_post.url,
            obj.reddit_post.url,
        )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(created_at__date=date.today()).order_by("-ranking")
