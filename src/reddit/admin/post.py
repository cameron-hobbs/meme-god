from django.contrib import admin

from src.reddit.models import RedditPost, RedditPostChangeLog


class RedditPostChangeLogInline(admin.TabularInline):
    extra = 1
    model = RedditPostChangeLog


@admin.register(RedditPost)
class RedditPostAdmin(admin.ModelAdmin):
    fields = (
        "subreddit",
        "author",
        "post_id",
        "is_video",
        "post_created_at",
        "url",
        "title",
        "score",
        "num_comments",
        "upvote_ratio",
        "total_awards_received",
    )
    list_display = (
        "title",
        "subreddit_category",
        "url",
        "score",
        "upvote_ratio",
        "num_comments",
    )
    list_filter = ("subreddit__category",)

    def subreddit_category(self, obj):
        return obj.subreddit.category if obj.subreddit.category else obj.subreddit.tag

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.order_by("-post_created_at", "-score")
        return queryset

    def view_url(self, obj):
        return f'<a href="{obj}">{obj}</a>'

    inlines = [RedditPostChangeLogInline]
