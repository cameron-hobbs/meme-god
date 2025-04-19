import logging
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from src.common.models import BaseChangeLog, BaseModel


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self) -> None:
        raise NotImplementedError


T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class BaseComparisonScraper(BaseScraper, ABC, Generic[T]):
    @property
    @abstractmethod
    def change_log_model(self) -> type[BaseChangeLog]: ...

    @property
    @abstractmethod
    def comparison_model(self) -> type[T]: ...

    def ignore_change_fields(self) -> set[str]:
        return {"id", "created_at", "updated_at", "change_log"}

    @property
    def comparison_fields(self) -> list[str]:
        return [
            field.name
            for field in self.comparison_model._meta.get_fields()
            if field.name not in self.ignore_change_fields()
        ]

    @abstractmethod
    def cancel_comparison(self, field: str, old_value: str, new_value: str) -> bool:
        return old_value == new_value

    def compare_changes(self, existing_instance: T, new_instance: T) -> None:
        changes = []
        for field in self.comparison_fields:
            old_value = getattr(existing_instance, field)
            new_value = getattr(new_instance, field)

            if self.cancel_comparison(field, old_value, new_value):
                continue

            logger.debug(
                "post changed: %s - field %s (%s -> %s)",
                existing_instance.post_id,
                field,
                old_value,
                new_value,
            )
            changes.append(
                self.change_log_model(
                    post=existing_instance,
                    field_changed=field,
                    old_value=str(old_value),
                    new_value=str(new_value),
                )
            )
        if not len(changes):
            logger.debug("no changes for post %s", existing_instance.post_id)
        self.change_log_model.objects.bulk_create(changes)
