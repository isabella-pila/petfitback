import bcrypt
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Type

class PasswordValidationError(Exception):
    pass

class Password:
    def __init__(self, value: str, hashed: bool = False):
        if not hashed:
            if not self._is_valid(value):
                raise ValueError("Password must be at least 8 characters and contain letters and numbers.")
            self._value = self._hash_password(value)
        else:
            self._value = value

    def _is_valid(self, password: str) -> bool:
        return len(password) >= 8 and any(c.isalpha() for c in password) and any(c.isdigit() for c in password)

    def _hash_password(self, password: str) -> str:
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_bytes.decode('utf-8')

    def verify(self, plain_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), self._value.encode('utf-8'))

    def hashed_value(self) -> str:
        return self._value

    def __eq__(self, other) -> bool:
        if isinstance(other, Password):
            return self._value == other._value
        if isinstance(other, str) and other.startswith("$2b$"):
            return self._value == other
        return NotImplemented

    def __str__(self) -> str:
        return "<HASHED_PASSWORD>"

    def __hash__(self) -> int:
        return hash(self._value)

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type, handler: GetCoreSchemaHandler) -> CoreSchema:
        def validate_from_str(value: str, _info) -> "Password":
            return cls(value, hashed=False)

        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(cls),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.plain_validator_function(validate_from_str)
                ])
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: instance.hashed_value(),
            )
        )
