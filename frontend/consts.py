from enum import Enum


CHAT_INTRO_TEXT = (
    "Hello and welcome to the Cosmo LLM Interface!\n\n"
    "Begin your journey by sharing your parametrization in LaTeX format. From there, "
    "our intuitive system will guide you through naming parameters, setting ranges, "
    "and visualizing outcomes. At any stage, "
    'you can type "/help" for assistance and "/reset" to reset the interface. \n\n'
    "Explore the cosmos with us – your discovery starts here!"
)

class ContentType(str, Enum):
    TEXT = "TEXT"
    COLLECTION = "COLLECTION"
    IMAGE = "IMAGE"
    DATA_TABLE = "DATA_TABLE"
