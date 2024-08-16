from typing import Type, Any
from enum import Enum
from fastapi import UploadFile
from pydantic_extra_types.color import Color
from apps.base import SpecialException


class DataTypes(Enum):
    FILE = ("file", (UploadFile,type(None)))
    STRING = ("string", (str,type(None)))
    NUMBER = ("number", (int,float,type(None))) # type: ignore
    COLOR = ("color", (Color,type(None)))

    def __new__(cls, value: str, typ: Type|tuple[Type, ...]):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.type = typ # type: ignore
        return obj

    @property
    def db_value(self):
        return self.value
    
    def convert(self, value: Any) -> Any:
        for t in (self.type if isinstance(self.type, tuple) else (self.type,)): # type: ignore
            try:
                if self == DataTypes.COLOR and isinstance(value, str):
                    return Color(value).as_hex()
                return t(value)
            except (ValueError, TypeError):
                continue
        raise SpecialException(f"Value {value} cannot be converted to {self.name}")