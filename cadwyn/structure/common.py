import datetime
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from typing import ParamSpec, TypeAlias, TypeVar

import packaging.version
from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    GetJsonSchemaHandler,
)
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from typing_extensions import Annotated

VersionedModel = BaseModel
_P = ParamSpec("_P")
_R = TypeVar("_R")
Endpoint: TypeAlias = Callable[_P, _R]


@dataclass(slots=True, kw_only=True)
class _HiddenAttributeMixin:
    is_hidden_from_changelog: bool = False


class _VersionTypePydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
            cls,
            _source_type: Any,
            _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def validate_from_version(value: str) -> packaging.version.Version:
            return packaging.version.Version(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_version),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(packaging.version.Version),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
            cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `int`
        return handler(core_schema.int_schema())


# We now create an `Annotated` wrapper that we'll use as the annotation for fields on `BaseModel`s, etc.
PydanticVersionType = Annotated[
    packaging.version.Version, _VersionTypePydanticAnnotation
]

VersionTypeVar = TypeVar('VersionTypeVar', datetime.date, packaging.version.Version)
VersionType = datetime.date | packaging.version.Version