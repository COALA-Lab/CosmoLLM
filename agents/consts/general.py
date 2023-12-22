from enum import Enum


class ResponseType(str, Enum):
    TEXT = "TEXT"
    FUNCTION = "FUNCTION"
    NONE = "NONE"
