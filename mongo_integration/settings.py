import os

from environs import Env


env = Env()
env.read_env(path=os.getcwd() + "/../.env")

MONGO_URL = env.str("MONGO_URL", "localhost:27017")
MONGO_USER = env.str("MONGO_USER", "")
MONGO_PASSWORD = env.str("MONGO_PASSWORD", "")
