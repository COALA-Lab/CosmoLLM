import os

from environs import Env


env = Env()
env.read_env(path=os.getcwd() + "/.env")


# OpenAI
OPENAI_API_KEY = env.str("OPENAI_API_KEY", "")
OPENAI_CHAT_GPT_MODEL = env.str("OPENAI_CHAT_GPT_MODEL", "gpt-3.5-turbo")


# LangChain
LANGCHAIN_CHAT_MODEL = env.str("LANGCHAIN_CHAT_MODEL", "gpt-3.5-turbo")
