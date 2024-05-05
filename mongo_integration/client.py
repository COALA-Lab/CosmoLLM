from pymongo import MongoClient
from pymongo.database import Database

from . import settings as mongo_settings
import settings as global_settings


class Mongo:
    instance: MongoClient = None

    def __init__(self):
        if not Mongo.instance:
            Mongo._create_instance()

    @staticmethod
    def _create_instance() -> None:
        Mongo.instance = MongoClient(
            mongo_settings.MONGO_URL,
            username=mongo_settings.MONGO_USER,
            password=mongo_settings.MONGO_PASSWORD,
        )

    @staticmethod
    def _get_db_name() -> str:
        deployment_id = global_settings.DEPLOYMENT_ID
        deployment_type = global_settings.DEPLOYMENT_TYPE

        if deployment_id and deployment_type:
            return f"{deployment_id}_{deployment_type}"
        else:
            return "cosmollm_local"

    @staticmethod
    def _get_db() -> Database:
        client = Mongo.instance
        db_name = Mongo._get_db_name()

        return client[db_name]

    def __getattr__(self, item):
        db = self._get_db()

        return getattr(db, item)

    def __setattr__(self, key, value):
        db = self._get_db()

        setattr(db, key, value)
