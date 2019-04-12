import datetime
import json as _json
import logging
from decimal import Decimal
from json import JSONEncoder as _JSONEncoder
from uuid import UUID

from enum import Enum

from sqlalchemy import inspect

from backend import log
from backend.models import Base

loads = _json.loads


class JSONEncoder(_JSONEncoder):
    """
    JSON Encoder for database models, datetimes, UUIDs, etc
    """

    continue_on_error = False

    def default(self, o):
        # disable method-hidden pylint: disable=E0202
        if isinstance(o, Base):
            return_fields = {}
            inspection = inspect(o)
            fields = [field for field in dir(o) if not field.startswith("_") and field != "metadata"]
            for field in fields:
                if field in inspection.unloaded:
                    continue
                data = o.__getattribute__(field)
                if callable(data):
                    continue
                try:
                    dumps(data)
                    return_fields[field] = data
                except ValueError as ex:
                    if not self.__class__.continue_on_error:
                        raise ex
            return return_fields
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, Decimal):
            return float(o)
        return o


def dumps(obj, continue_on_error=False):
    """
    Dump a dict to JSON string
    :param obj: object to dump
    :param continue_on_error:
    :return:
    """
    prev_value = JSONEncoder.continue_on_error
    try:
        JSONEncoder.continue_on_error = continue_on_error
        return _json.dumps(obj, cls=JSONEncoder)
    except ValueError as ex:
        log.warning("Failed object: {}".format(obj))
        raise ex
    finally:
        JSONEncoder.continue_on_error = prev_value
