from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, NamedTuple, Optional, Dict

import monkey.token as token


class Node(ABC):
    @abstractmethod
    def token_literal(self) -> str:
        ...

    @abstractmethod
    def __str__(self) -> str:
        ...


@dataclass
class Program(Node):
    statements: List[Node] = field(default_factory=list)

    def token_literal(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ""

    def __str__(self) -> str:
        return "".join([str(s) for s in self.statements])


@dataclass
class Identifier(Node):
    token: token.Token
    value: str

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.value


@dataclass
class LetStatement(Node):
    token: token.Token
    name: Identifier
    value: Node

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"{self.token_literal()} {str(self.name)} = {str(self.value)}"


@dataclass
class ReturnStatement(Node):
    token: token.Token
    value: Identifier

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"{self.token_literal()} {str(self.value)};"


@dataclass
class ExpressionStatement(Node):
    token: token.Token
    expression: Node

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return str(self.expression)


@dataclass
class IntegerLiteral(Node):
    token: token.Token
    value: int

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.token.literal


@dataclass
class PrefixExpression(Node):
    token: token.Token
    operator: str
    right: Node

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({self.operator}{str(self.right)})"


@dataclass
class InfixExpression(Node):
    token: token.Token
    left: Node
    operator: str
    right: Node

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"({str(self.left)} {self.operator} {str(self.right)})"


@dataclass
class Boolean(Node):
    token: token.Token
    value: bool

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return self.token.literal


@dataclass
class BlockStatement(Node):
    token: token.Token
    statements: List[Node]

    def statement_node(self):
        pass

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return "\n".join([str(s) for s in self.statements])


@dataclass
class IfExpression(Node):
    token: token.Token
    condition: Node
    consequence: BlockStatement
    alternative: Optional[BlockStatement]

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        if self.alternative is not None:
            return f"if\n{str(self.condition)} {str(self.consequence)} else\n{str(self.alternative)}"
        else:
            return f"if\n{str(self.condition)} {str(self.consequence)}"


@dataclass
class FunctionLiteral(Node):
    token: token.Token
    params: List[Identifier]
    body: BlockStatement

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"{self.token_literal()}({', '.join([str(s) for s in self.params])}){str(self.body)}"


@dataclass
class CallExpression(Node):
    token: token.Token
    function: Node
    arguments: List[Node]

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f"{str(self.function)}({', '.join([str(s) for s in self.arguments])})"


@dataclass
class StringLiteral(Node):
    token: token.Token
    value: str

    def token_literal(self) -> str:
        return self.token.literal

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.token.literal


@dataclass
class ArrayLiteral(Node):
    token: token.Token
    elements: List[Node]

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        return f'[{", ".join([str(e) for e in self.elements])}]'


@dataclass
class IndexExpression(Node):
    token: token.Token
    left: Node
    index: Node

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self):
        return f"({str(self.left)}[{str(self.index)}])"


@dataclass
class HashLiteral(Node):
    token: token.Token
    pairs: Dict[Node, Node]

    def token_literal(self) -> str:
        return self.token.literal

    def __str__(self) -> str:
        # [TODO] This is pretty messy
        return str({str(k): str(v) for k, v in self.pairs.items()})
