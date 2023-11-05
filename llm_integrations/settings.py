from environs import Env

from . import consts


env = Env()
env.read_env()


# General
OPENAI_API_KEY = env.str("OPENAI_API_KEY")
HISTORY_LENGTH = env.int("HISTORY_LENGTH", 20)


# OpenAI
OPENAI_CHAT_GPT_MODEL = env.str("OPENAI_CHAT_GPT_MODEL", "gpt-3.5-turbo")
OPENAI_CHAT_GPT_INTRO_PROMPT = env.str("OPENAI_CHAT_GPT_INTRO_PROMPT", consts.INTRO_PROMPT)


# LangChain
LANGCHAIN_CHAT_MODEL = env.str("LANGCHAIN_CHAT_MODEL", "gpt-3.5-turbo")
LANGCHAIN_CHAT_INTRO_PROMPT = env.str("LANGCHAIN_CHAT_INTRO_PROMPT", consts.INTRO_PROMPT)
