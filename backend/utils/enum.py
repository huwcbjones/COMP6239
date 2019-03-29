import enum as _enum
from typing import Set


class Enum(_enum.Enum):

    @classmethod
    def values(cls) -> Set:
        if not hasattr(cls, "__values__"):
            setattr(cls, "__values__", set(i.value for i in cls))
        return getattr(cls, "__values__")

    @classmethod
    def contains(cls, value):
        return value in cls.values()
