import logging
import os
from io import BytesIO
from urllib.parse import urlparse

from asgiref.sync import async_to_sync

import requests
from django.utils import timezone

from src.media_sender.models import SuggestedMedia
from src.media_sender.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)


def _filename_from_url(url):
    return os.path.basename(urlparse(url).path)


def send_media(suggested_media_id: int) -> None:
    logger.info("Processing suggested media: %s", suggested_media_id)
    suggested_media = SuggestedMedia.objects.get(id=suggested_media_id)

    data = BytesIO()

    if not suggested_media.is_video:
        response = requests.get(suggested_media.url)
        data.write(response.content)
    else:
        # todo: fix this, doesn't work
        response = requests.get(suggested_media.url, stream=True)
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive chunks
                data.write(chunk)

    if not suggested_media.is_video:
        data.name = _filename_from_url(suggested_media.url)
    else:
        data.name = f"{suggested_media.url.strip('/')[-1]}.mp4"
    data.seek(0)

    response.raise_for_status()

    bot = TelegramBot()

    if not suggested_media.is_video:
        async_to_sync(bot.send_image_msg)(
            suggested_media.topic, data, suggested_media.title
        )
    else:
        async_to_sync(bot.send_video_msg)(
            suggested_media.topic, data, suggested_media.title
        )

    suggested_media.sent_to_telegram_at = timezone.now()
    suggested_media.save()
