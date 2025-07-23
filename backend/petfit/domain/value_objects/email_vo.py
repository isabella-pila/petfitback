import re
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

class EmailValidationError(Exception):
    pass

class Email:
    def __init__(self, value: str):
        if not self._is_valid(value):
            raise ValueError("Invalid email format.")
        self._value = value

    def _is_valid(self, value: str) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, value) is not None

    def __str__(self) -> str:
        return self._value

    def __eq__(self, other) -> bool:
        if isinstance(other, Email):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return NotImplemented

    def __hash__(self) -> int:
        return hash(self._value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type, handler: GetCoreSchemaHandler) -> CoreSchema:
        def validate_from_str(value: str, _info) -> "Email":
            return cls(value)

        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.plain_validator_function(validate_from_str)
                ])
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance),
            )
        )
