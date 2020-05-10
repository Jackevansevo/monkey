from typing import List, Dict, Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass

from monkey import ast as ast

ObjectType = str

ARRAY_OBJ = "ARRAY"
HASH_OBJ = "HASH"
STRING_OBJ = "STRING"
BUILTIN_OBJ = "BUILTIN"
FUNCTION_OBJ = "FUNCTION"
ERROR_OBJ = "ERROR"
RETURN_VALUE_OBJ = "RETURN_VALUE"
INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
NULL_OBJ = "NULL"


class Object(ABC):
    @abstractmethod
    def object_type(self) -> ObjectType:
        ...

    @abstractmethod
    def inspect(self) -> str:
        ...


@dataclass
class Integer(Object):
    value: int

    def object_type(self) -> ObjectType:
        return INTEGER_OBJ

    def inspect(self) -> str:
        return str(self.value)


@dataclass
class Boolean(Object):
    value: bool

    def inspect(self) -> str:
        return str(self.value).lower()

    def __bool__(self) -> bool:
        return self.value

    def object_type(self) -> ObjectType:
        return BOOLEAN_OBJ


@dataclass
class NullObject(Object):
    def inspect(self) -> str:
        return "null"

    def __bool__(self) -> bool:
        return False

    def object_type(self) -> ObjectType:
        return NULL_OBJ


@dataclass
class ReturnValue(Object):
    value: Object

    def inspect(self) -> str:
        return self.value.inspect()

    def object_type(self) -> ObjectType:
        return RETURN_VALUE_OBJ


@dataclass
class Error(Object):
    msg: str

    def inspect(self) -> str:
        return "ERROR: " + self.msg

    def object_type(self) -> ObjectType:
        return ERROR_OBJ


@dataclass
class Function(Object):
    params: List[ast.Identifier]
    env: Dict
    body: ast.BlockStatement

    def inspect(self) -> str:
        return f"fn({', '.join([str(s) for s in self.params])}){str(self.body)}"

    def object_type(self) -> ObjectType:
        return FUNCTION_OBJ


@dataclass
class String(Object):
    value: str

    def object_type(self) -> ObjectType:
        return STRING_OBJ

    def inspect(self) -> str:
        return self.value


@dataclass
class Builtin(Object):
    fn: Callable[[List[Object]], Object]

    def object_type(self) -> ObjectType:
        return BUILTIN_OBJ

    def inspect(self) -> str:
        return "builtin function"


@dataclass
class Array(Object):
    elements: List[Object]

    def object_type(self) -> ObjectType:
        return ARRAY_OBJ

    def inspect(self) -> str:
        return f'[{", ".join([e.inspect() for e in self.elements])}]'


@dataclass
class Hash(Object):
    pairs: Dict

    def object_type(self) -> ObjectType:
        return HASH_OBJ

    def inspect(self) -> str:
        return "hello world"


NULL = NullObject()
TRUE = Boolean(True)
FALSE = Boolean(False)
