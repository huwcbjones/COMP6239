import random
import re
import string
import uuid
from typing import Optional, Any

from .regex import uuid as uuid_regex

_uuid_regex = re.compile(uuid_regex)


def random_string(length):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


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
    try:
        return uuid.UUID(uuid_obj)
    except ValueError:
        pass


def str_to_bool(s: str) -> bool:
    if isinstace(s, bool):
        return s
    if s.lower() in ("true", "t", "yes", "y"):
        return True
    elif s.lower() in ("false", "f", "no", "n"):
        return False
    else:
        raise ValueError("'{}' is not a valid boolean value".format(s))


def str_to_int(s: str) -> int:
    if isinstance(s, int):
        return s
    return int(s)
