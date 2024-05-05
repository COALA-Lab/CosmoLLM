import os

from environs import Env


env = Env()
env.read_env(path=os.getcwd() + "/../.env")

ADMIN_USER = env.str("ADMIN_USER", "admin")
ADMIN_PASSWORD = env.str("ADMIN_PASSWORD", "admin")
