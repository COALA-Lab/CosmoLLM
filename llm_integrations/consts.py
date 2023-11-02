# General
INTRO_PROMPT = """
    You are an AI assistant knowledgeable in the use of 'CosmoLLM', a physics library written in Python.
    You are talking to a user that needs your help to use the library, but has no programming knowledge.
"""


# LangChain
LANGCHAIN_MEMORY_KEY = "chat_memory"
LANGCHAIN_HUMAN_MESSAGE_KEY = "human_message"
LANGCHAIN_HUMAN_MESSAGE_TEMPLATE = "{" + LANGCHAIN_HUMAN_MESSAGE_KEY + "}"
