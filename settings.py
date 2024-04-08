import os

from environs import Env


env = Env()
env.read_env(path=os.getcwd() + "/.env")

MPI_HOSTS = env.list("MPI_HOSTS", "")
