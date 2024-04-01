from django.db import models

# Create your models here.
import uuid as uuid
from simple_history.models import HistoricalRecords
from datetime import datetime


class BaseUUIDModel(models.Model):
    """
    Base UUID model that represents a unique identifier for a given model.
    """
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, db_index=True, editable=False)
    is_active = models.BooleanField(default=True)
    __history_date = datetime.now()
    history = HistoricalRecords(inherit=True)

    @property
    def _history_date(self):
        return self.__history_date

    @_history_date.setter
    def _history_date(self, value):
        self.__history_date = value

    class Meta:
        abstract = True

    @classmethod
    def readByToken(cls, token: str, is_change=False):
        """ take an object by token"""
        if is_change is False:
            return cls.objects.get(id=token)
        return cls.objects.select_for_update().get(id=token)
