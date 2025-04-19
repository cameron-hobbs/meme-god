from django.contrib import admin

from src.common.admin import ReadOnlyModelAdmin
from src.media_sender.models import SuggestedMedia


@admin.register(SuggestedMedia)
class SuggestedMediaAdmin(ReadOnlyModelAdmin):
    fields = ("topic", "title", "url", "sent_to_telegram_at")
    list_display = ("id", "topic", "title", "url", "sent_to_telegram_at")
