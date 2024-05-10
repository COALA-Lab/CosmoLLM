from abc import ABC
from enum import Enum
from typing import List, Optional

import streamlit as st
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from models.db_model import DBModel

VIEW_IGNORED_FIELDS = ["subscribers"]


class FieldType(str, Enum):
    STRING = "String"
    NUMBER = "Number"
    INTEGER = "Integer"
    LIST = "List"


class Field(BaseModel):
    id: str
    displayName: str
    defaultValue: str
    required: bool
    type: FieldType


class View(DBModel, ABC):
    @classmethod
    def get_fields(cls) -> List[Field]:
        fields = []

        for field_name, field_info in cls.model_fields.items():
            if field_name.startswith("_"):
                continue
            if field_name in VIEW_IGNORED_FIELDS:
                continue

            field_info: FieldInfo

            default_value = field_info.get_default()
            if default_value is None or field_info.is_required():
                default_value = ""

            fields.append(
                Field(
                    id=field_name,
                    displayName=View._field_id_to_name(field_name),
                    defaultValue=str(default_value),
                    required=field_info.is_required(),
                    type=View._field_type_to_enum(field_info)
                )
            )

        return fields

    @classmethod
    def execute_form(cls, old_model: Optional[DBModel] = None) -> Optional[DBModel]:
        fields = cls.get_fields()
        model = None
        results = {}

        form_key = "new"
        if old_model is not None:
            form_key = getattr(old_model, old_model.get_primary_key())

        with st.form(key=form_key):
            for field in fields:
                default_value = field.defaultValue
                if old_model is not None:
                    default_value = getattr(old_model, field.id)

                field_slug = field.id.lower()
                if "password" in field_slug or "token" in field_slug or "secret" in field_slug:
                    input_type = "password"
                else:
                    input_type = "default"

                label = field.displayName + f" ({field.type.value})" + ("*" if field.required else "")

                if field.type == FieldType.STRING:
                    result = st.text_input(label, value=default_value, type=input_type)
                    if result:
                        results[field.id] = result
                elif field.type == FieldType.INTEGER:
                    result = st.number_input(label, value=int(default_value), step=int(1), format="%d")
                    if result is not None:
                        results[field.id] = result
                elif field.type == FieldType.NUMBER:
                    result = st.number_input(label, value=default_value)
                    if result is not None:
                        results[field.id] = result
                elif field.type == FieldType.LIST:
                    default_value = ",".join(default_value)
                    result = st.text_input(label, value=default_value)
                    results[field.id] = result.split(",")

            submit = st.form_submit_button("Submit")

        if submit and results:
            try:
                model = cls(**results)
            except Exception as e:
                st.error(f"Failed to update object! error={e}")
                for field in fields:
                    if field.required and field.id not in results:
                        st.error(f"Field {field.displayName} is required!")

        return model

    def get_field_diff(self, other: 'View') -> List[str]:
        fields = self.get_fields()
        different_fields = []

        for field in fields:
            if getattr(self, field.id) != getattr(other, field.id):
                different_fields.append(field.id)

        return different_fields

    @staticmethod
    def _field_id_to_name(field_id: str) -> str:
        words = []
        current_word = ""
        for letter in field_id:
            if letter.isupper():
                words.append(current_word)
                current_word = letter.lower()
            else:
                current_word += letter

        words.append(current_word)

        return (" ".join(words)).capitalize()

    @staticmethod
    def _field_type_to_enum(field_info: FieldInfo) -> FieldType:
        annotation = field_info.annotation

        if str(annotation).startswith("typing.Optional"):
            annotation = annotation.__args__[0]

        if annotation == str:
            return FieldType.STRING
        elif annotation == int:
            return FieldType.INTEGER
        elif annotation == float:
            return FieldType.NUMBER
        elif str(annotation).startswith("typing.List") or str(annotation).startswith("list"):
            return FieldType.LIST
        else:
            raise Exception(f"Unknown field type {field_info.annotation}!")
