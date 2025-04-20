import logging
from typing import Any

from django.core.management import BaseCommand
from src.media_sender.tasks import make_daily_suggestions

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        logger.info("Making daily suggestions")
        make_daily_suggestions.delay()
