from enum import Enum


CHAT_INTRO_TEXT = "You are now chatting with a GPT powered chatbot."


class ContentType(str, Enum):
    TEXT = "TEXT"
    COLLECTION = "COLLECTION"
    IMAGE = "IMAGE"
    DATA_TABLE = "DATA_TABLE"
