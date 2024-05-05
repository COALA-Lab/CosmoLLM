from abc import ABC

from pydantic import BaseModel
from pymongo.results import UpdateResult, DeleteResult
from pymongo.collection import Collection

from mongo_integration.client import Mongo


class DBModel(BaseModel, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._create_index()

    def save(self) -> bool:
        collection = self._get_collection()
        primary_key = self.get_primary_key()
        data = self.model_dump()

        result: UpdateResult = collection.update_one(
            {primary_key: data[primary_key]},
            {"$set": data},
            upsert=True
        )

        created = False

        if result.matched_count == 0 and result.upserted_id is not None:
            created = True
        elif result.modified_count == 0:
            raise Exception("Failed to save model!")

        return created

    def delete(self) -> bool:
        collection = self._get_collection()
        primary_key = self.get_primary_key()
        data = self.model_dump()

        result: DeleteResult = collection.delete_one({primary_key: data[primary_key]})

        if result.deleted_count == 0:
            raise Exception("Failed to delete model!")

        return True

    @classmethod
    def get(cls, **filter) -> BaseModel:
        results = list(cls.filter(**filter))

        if len(results) == 0:
            raise Exception("Model not found!")
        elif len(results) > 1:
            raise Exception(f"Multiple models found for model {cls.__name__} with params {filter}!")

        return results[0]

    @classmethod
    def filter(cls, **filter) -> list[BaseModel]:
        collection = cls._get_collection()

        demangled_filter = {}

        for key in filter:
            demangled_key = key.replace("__", ".")
            demangled_filter[demangled_key] = filter[key]

        data = collection.find(demangled_filter)
        for raw_model in data:
            yield cls(**raw_model)

    @classmethod
    def get_primary_key(cls) -> str:
        if "id" in cls.model_fields:
            return "id"

        raise Exception("Primary key not found!")

    @classmethod
    def get_collection_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def _get_collection(cls) -> Collection:
        collection_name = cls.get_collection_name()
        return Mongo()[collection_name]

    @classmethod
    def _create_index(cls):
        collection = cls._get_collection()
        primary_key = cls.get_primary_key()
        collection.create_index(primary_key, unique=True)
