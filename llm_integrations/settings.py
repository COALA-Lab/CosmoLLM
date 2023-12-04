from environs import Env

from . import consts


env = Env()
env.read_env()


# General
OPENAI_API_KEY = env.str("OPENAI_API_KEY")
MAX_HISTORY_LENGTH = env.int("MAX_HISTORY_LENGTH", 4000)

# Prompts
PARAMETRIZATION_GENERATION_SYSTEM_PROMPT = env.str(
    "PARAMETRIZATION_GENERATION_SYSTEM_PROMPT", consts.PARAMETRIZATION_GENERATION_SYSTEM_PROMPT
)
PRIORI_GENERATION_SYSTEM_PROMPT = env.str("PRIORI_GENERATION_SYSTEM_PROMPT", consts.PRIORI_GENERATION_SYSTEM_PROMPT)


# OpenAI
OPENAI_CHAT_GPT_MODEL = env.str("OPENAI_CHAT_GPT_MODEL", "gpt-3.5-turbo")
OPENAI_CHAT_GPT_INTRO_PROMPT = env.str("OPENAI_CHAT_GPT_INTRO_PROMPT", consts.INTRO_PROMPT)


# LangChain
LANGCHAIN_CHAT_MODEL = env.str("LANGCHAIN_CHAT_MODEL", "gpt-3.5-turbo")
# TODO: discuss -> is there any reason to separate this by implementation, especially since all of them use ChatGPT
LANGCHAIN_CHAT_INTRO_PROMPT = env.str("LANGCHAIN_CHAT_INTRO_PROMPT", consts.INTRO_PROMPT)
