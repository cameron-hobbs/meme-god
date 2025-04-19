from django.contrib import admin

from src.reddit.models import RedditSub


@admin.register(RedditSub)
class RedditSubAdmin(admin.ModelAdmin):
    fields = ("tag", "category")
    list_display = ("id", "category", "tag")
