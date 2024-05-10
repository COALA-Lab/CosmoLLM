from abc import ABC
from enum import Enum
from typing import Callable, List, Optional

from pydantic import BaseModel
from pymongo.results import UpdateResult, DeleteResult
from pymongo.collection import Collection

from mongo_integration.client import Mongo


class ChangeType(str, Enum):
    CREATE = "Create"
    UPDATE = "Update"
    DELETE = "Delete"


class Subscriber(BaseModel):
    collection_name: str
    primary_key: str
    primary_value: str
    receiver_name: str = "on_event"


class DBModel(BaseModel, ABC):
    subscribers: List[Subscriber] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._create_index()

    def save(self) -> bool:
        collection = self._get_collection()
        primary_key = self.get_primary_key()
        data = self.model_dump()

        result: UpdateResult = collection.update_one(
            {primary_key: self.get_primary_value()},
            {"$set": data},
            upsert=True
        )

        created = False

        if result.matched_count == 0 and result.upserted_id is not None:
            created = True
        elif result.modified_count == 0:
            raise Exception("Model not changed!")

        self.notify(ChangeType.CREATE if created else ChangeType.UPDATE)

        return created

    def delete(self) -> bool:
        collection = self._get_collection()
        primary_key = self.get_primary_key()

        result: DeleteResult = collection.delete_one({primary_key: self.get_primary_value()})

        if result.deleted_count == 0:
            raise Exception("Failed to delete model!")

        self.notify(ChangeType.DELETE)

        return True

    @classmethod
    def get(cls, **filter) -> 'DBModel':
        results = list(cls.filter(**filter))

        if len(results) == 0:
            raise Exception("Model not found!")
        elif len(results) > 1:
            raise Exception(f"Multiple models found for model {cls.__name__} with params {filter}!")

        return results[0]

    @classmethod
    def filter(cls, **filter) -> list['DBModel']:
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

    def get_primary_value(self) -> str:
        return getattr(self, self.get_primary_key())

    @classmethod
    def get_collection_name(cls) -> str:
        return cls.__name__.lower()

    def subscribe(self, subject: 'DBModel', receiver_name: Optional[str] = None) -> None:
        if receiver_name is None:
            receiver_name = "on_event"

        subscriber = Subscriber(
            id=subject.get_collection_name() + subject.get_primary_value(),
            collection_name=subject.get_collection_name(),
            primary_key=subject.get_primary_key(),
            primary_value=subject.get_primary_value(),
            receiver_name=receiver_name
        )
        self.subscribers.append(subscriber)

    def unsubscribe(self, subject: 'DBModel') -> None:
        self.subscribers = [
            subscriber for subscriber in self.subscribers
            if subscriber.id != subject.get_collection_name() + subject.get_primary_value()
        ]

    def notify(self, change_type: ChangeType) -> None:
        for subscriber in self.subscribers:
            try:
                model = Mongo()[subscriber.collection_name].find_one({subscriber.primary_key: subscriber.primary_value})
                getattr(model, subscriber.receiver_name)(self, change_type)
            except Exception as e:
                raise Exception(
                    f"Failed to notify subscriber "
                    f"{subscriber.collection_name}:{subscriber.primary_value} with error {e}"
                )

    @classmethod
    def _get_collection(cls) -> Collection:
        collection_name = cls.get_collection_name()
        return Mongo()[collection_name]

    @classmethod
    def _create_index(cls):
        collection = cls._get_collection()
        primary_key = cls.get_primary_key()
        collection.create_index(primary_key, unique=True)
