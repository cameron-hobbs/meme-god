__all__ = ["RedditUserAdmin"]

from django.contrib import admin

from src.common.admin import ReadOnlyModelAdmin
from src.reddit.models import RedditUser


@admin.register(RedditUser)
class RedditUserAdmin(ReadOnlyModelAdmin):
    fields = (
        "name",
        "full_name",
    )
    list_display = ("id", "name", "created_at")
    # todo: inline for posts
