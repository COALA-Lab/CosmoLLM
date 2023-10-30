from environs import Env


env = Env()
env.read_env()


# General
OPENAI_API_KEY = env.str("OPENAI_API_KEY")


# GPT Chat
GPT_CHAT_MODEL = env.str("GPT_CHAT_MODEL", "gpt-3.5-turbo")
GPT_CHAT_INTRO_PROMPT = env.str(
    "GPT_CHAT_INTRO_PROMPT",
    "You are an AI assistant knowledgeable in the use of 'CosmoLLM', a physics library written in Python. "
    "You are talking to a user that needs your help to use the library, but has no programming knowledge."
)
