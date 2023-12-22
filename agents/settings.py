import os

from environs import Env

from . import consts


env = Env()
env.read_env(path=os.getcwd() + "/.env")


# General
MAX_HISTORY_LENGTH = env.int("MAX_HISTORY_LENGTH", 4000)

# Prompts
PARAMETRIZATION_GENERATION_SYSTEM_PROMPT = env.str(
    "PARAMETRIZATION_GENERATION_SYSTEM_PROMPT", consts.PARAMETRIZATION_GENERATION_SYSTEM_PROMPT
)
PRIORI_GENERATION_SYSTEM_PROMPT = env.str("PRIORI_GENERATION_SYSTEM_PROMPT", consts.PRIORI_GENERATION_SYSTEM_PROMPT)