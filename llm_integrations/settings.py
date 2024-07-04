import os

from environs import Env

root_dir = os.path.dirname(__file__) + "/.."
env = Env()
env.read_env(path=root_dir + "/.env")


# OpenAI
OPENAI_API_KEY = env.str("OPENAI_API_KEY", "")
OPENAI_CHAT_GPT_MODEL = env.str("OPENAI_CHAT_GPT_MODEL", "gpt-4o")


# LangChain
LANGCHAIN_CHAT_MODEL = env.str("LANGCHAIN_CHAT_MODEL", "gpt-4o")
