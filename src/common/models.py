from django.db import models
from seal.models import SealableModel


class BaseCreatedAtModel(SealableModel):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class BaseModel(BaseCreatedAtModel):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseChangeLog(BaseCreatedAtModel):
    field_changed = models.CharField(max_length=255, null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class BaseRankedPost(BaseCreatedAtModel):
    ranking = models.FloatField(default=0)

    class Meta:
        abstract = True
