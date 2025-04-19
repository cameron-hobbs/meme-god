__all__ = ["TopicChannelAdmin"]

from django.contrib import admin

from src.media_sender.models import TopicChannel


@admin.register(TopicChannel)
class TopicChannelAdmin(admin.ModelAdmin):
    fields = (
        "topic",
        "channel",
    )
    list_display = ("id", "topic", "channel")
