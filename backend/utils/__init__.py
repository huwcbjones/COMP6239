import re
import uuid
from typing import Optional, Any

from .regex import uuid as uuid_regex

_uuid_regex = re.compile(uuid_regex)


def convert_to_uuid(uuid_obj: Any) -> Optional[uuid.UUID]:
    """
    Tries to convert an object into a UUID
    :param uuid_obj:
    :return:
    """
    if isinstance(uuid_obj, uuid.UUID):
        return uuid_obj

    if uuid_obj is None:
        return None

    if isinstance(uuid_obj, str):
        return convert_string_to_uuid(uuid_obj)

    return None


def convert_string_to_uuid(uuid_obj: str) -> Optional[uuid.UUID]:
    uuid_obj = uuid_obj.lower()
    if _uuid_regex.match(uuid_obj):
        try:
            return uuid.UUID(uuid_obj)
        except ValueError:
            pass
