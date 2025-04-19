import logging
import os
from io import BytesIO
from typing import Any

from telegram import Bot
from telegram.error import TimedOut, TelegramError

from src.common.choices import Topic
from src.media_sender.models import TopicChannel


logger = logging.getLogger(__name__)


class TelegramBotError(Exception):
    def __init__(self, e: TelegramError):
        self.e = e


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
        self.topic_channels: dict[Topic, str] = {
            item["topic"]: item["channel"]
            for item in TopicChannel.objects.values("topic", "channel")
        }

    async def send_msg(self, topic: Topic, msg: str) -> None:
        if (channel := self.topic_channels.get(topic)) is None:
            logger.info("Could not find channel for topic %s", topic)
            return

        try:
            await self.bot.send_message(channel, msg)
            logger.debug("Sent message %s to channel %s", msg, channel)
        except TimedOut as e:
            raise TelegramBotError(e)

    async def send_image_msg(
        self, topic: Topic, image_bytes: BytesIO, caption: str, **kwargs: Any
    ) -> None:
        if (channel := self.topic_channels.get(topic)) is None:
            logger.info("Could not find channel for topic %s", topic)
            return

        try:
            await self.bot.send_photo(channel, image_bytes, caption, **kwargs)
            logger.debug("Sent image to channel %s", channel)
        except TimedOut as e:
            raise TelegramBotError(e)

    async def send_video_msg(
        self, topic: Topic, video_bytes: BytesIO, caption: str, **kwargs: Any
    ) -> None:
        if (channel := self.topic_channels.get(topic)) is None:
            logger.info("Could not find channel for topic %s", topic)
            return

        try:
            await self.bot.send_video(channel, video_bytes, caption=caption, **kwargs)
            logger.debug("sent video to channel %s", channel)
        except TimedOut as e:
            raise TelegramBotError(e)
