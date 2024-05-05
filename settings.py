import os
from enum import Enum

from environs import Env


env = Env()
env.read_env(path=os.getcwd() + "/.env")

MPI_HOSTS = env.list("MPI_HOSTS", "")
MPI_HOST_SLOTS = env.int("MPI_HOST_SLOTS", 2)

DEPLOYMENT_ID = env.str("DEPLOYMENT_ID", "")
DEPLOYMENT_TYPE = env.str("DEPLOYMENT_TYPE", "")


class DeploymentType(str, Enum):
    COMPUTE = "compute"
    GUI = "gui"
    ADMIN = "admin"
