import logging
import os
import subprocess
import tempfile

from io import BytesIO
import random
from urllib.parse import urlparse

from asgiref.sync import async_to_sync

import requests
from bs4 import BeautifulSoup
from django.utils import timezone

from src.common.choices import Topic
from src.media_sender.models import SuggestedMedia
from src.media_sender.telegram_bot import TelegramBot

logger = logging.getLogger(__name__)


def _filename_from_url(url):
    return os.path.basename(urlparse(url).path)


_POPULAR_HASHTAGS = {
    Topic.MEMES: [
        "#memes",
        "#memesdaily",
        "#funny",
        "#funnymemes",
        "#memelord",
        "#memeoftheday",
        "#memesofinstagram",
        "#instamemes",
        "#lol",
        "#humor",
        "#memelife",
        "#dankmemes",
    ],
    Topic.LONDON: [
        "#london",
        "#londonlife",
        "#citylife",
        "#londoncity",
        "#thisislondon",
        "#londonlove",
        "#londoncalling",
    ],
}


def _download_m3u8_to_memory(m3u8_url: str) -> BytesIO | None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
        temp_path = tmp_file.name

    try:
        ffmpeg_command = [
            "ffmpeg",
            "-y",
            "-i",
            m3u8_url,
            "-c:v",
            "libx264",
            "-c:a",
            "aac",
            "-f",
            "mp4",
            "-movflags",
            "+faststart",
            temp_path,
        ]
        result = subprocess.run(
            ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr.decode()}")

        with open(temp_path, "rb") as f:
            video_data = BytesIO(f.read())
            return video_data

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def send_media(suggested_media_id: int) -> None:
    logger.info("Processing suggested media: %s", suggested_media_id)
    suggested_media = SuggestedMedia.objects.get(id=suggested_media_id)

    data = BytesIO()

    if not suggested_media.is_video:
        response = requests.get(suggested_media.url)
        data.write(response.content)
    else:
        response = requests.get(suggested_media.url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")
        vid_sources = soup.find_all("source")
        if not vid_sources:
            logger.debug("Could not find any video sources")
            return
        src = vid_sources[0].get("src")
        logger.debug("Source for vid is %s", src)
        data = _download_m3u8_to_memory(src)

    if not suggested_media.is_video:
        data.name = _filename_from_url(suggested_media.url)
    else:
        data.name = f"{suggested_media.url.strip('/')[-1]}.mp4"
    data.seek(0)

    response.raise_for_status()

    bot = TelegramBot()

    curated_title = suggested_media.title

    curated_title += "\n"
    curated_title += " ".join(
        random.sample(_POPULAR_HASHTAGS[suggested_media.topic], random.randint(3, 5))
    )

    if not suggested_media.is_video:
        async_to_sync(bot.send_image_msg)(suggested_media.topic, data, curated_title)
    else:
        async_to_sync(bot.send_video_msg)(suggested_media.topic, data, curated_title)

    suggested_media.sent_to_telegram_at = timezone.now()
    suggested_media.save()
