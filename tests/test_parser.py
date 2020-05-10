from typing import NamedTuple, cast, List, Any

import pytest

from monkey.lexer import Lexer
from monkey.parser import Parser
from monkey.token import Token
import monkey.ast as ast


def check_let_statement(stmt, name: str):
    assert stmt.token_literal() == "let"

    assert isinstance(stmt, ast.LetStatement)

    assert stmt.name.value == name

    assert stmt.name.token_literal() == name


@pytest.mark.parametrize(
    "source,expected_identifier,expected_value",
    [
        ("let x = 5;", "x", 5),
        ("let y = true;", "y", True),
        ("let foobar = y;", "foobar", "y"),
    ],
)
def test_let_statements(source, expected_identifier, expected_value):
    l = Lexer(source)
    p = Parser(l)

    program = p.parse_program()
    assert p.errors == []

    assert program is not None

    assert len(program.statements) == 1

    stmt = program.statements[0]

    check_let_statement(stmt, expected_identifier)

    assert stmt.value.value == expected_value


def test_return_statements():
    source = """
    return 5;
    return 10;
    return 993322;
    """

    l = Lexer(source)
    p = Parser(l)

    program = p.parse_program()
    assert p.errors == []

    assert program is not None

    assert len(program.statements) == 3

    for stmt in program.statements:
        assert type(stmt) == ast.ReturnStatement
        assert stmt.token_literal() == "return"


def test_identifier_expression():
    source = "foobar;"

    l = Lexer(source)
    p = Parser(l)

    program = p.parse_program()
    assert p.errors == []

    assert len(program.statements) == 1

    stmt = program.statements[0]

    assert type(stmt) == ast.ExpressionStatement

    assert type(stmt.expression) == ast.Identifier

    ident = stmt.expression

    assert ident.value == "foobar"
    assert ident.token_literal() == "foobar"


def test_integer_literals():
    source = "5;"

    l = Lexer(source)
    p = Parser(l)

    program = p.parse_program()
    assert p.errors == []

    assert len(program.statements) == 1

    stmt = program.statements[0]

    assert type(stmt) == ast.ExpressionStatement

    assert type(stmt.expression) == ast.IntegerLiteral

    literal = stmt.expression

    assert literal.value == 5
    assert literal.token_literal() == "5"


@pytest.mark.parametrize(
    "source,operator,expected",
    [
        ("!5;", "!", 5),
        ("-15;", "-", 15),
    ],
)
def test_prefix_expressions(source, operator, expected):
    l = Lexer(source)
    p = Parser(l)

    program = p.parse_program()
    assert p.errors == []

    assert len(program.statements) == 1

    stmt = program.statements[0]

    assert type(stmt) == ast.ExpressionStatement

    assert type(stmt.expression) == ast.PrefixExpression

    assert stmt.expression.operator == operator

    assert stmt.expression.right.value == expected


@pytest.mark.parametrize(
    "source,left,operator,right",
    [
        ("5 + 5", 5, "+", 5),
        ("5 - 5", 5, "-", 5),
        ("5 * 5", 5, "*", 5),
        ("5 / 5", 5, "/", 5),
        ("5 > 5", 5, ">", 5),
        ("5 < 5", 5, "<", 5),
        ("5 == 5", 5, "==", 5),
        ("5 != 5", 5, "!=", 5),
    ],
)
def test_infix_expressions(source, left, operator, right):
    l = Lexer(source)
    p = Parser(l)
    program = p.parse_program()
    assert p.errors == []

    assert len(program.statements) == 1

    stmt = program.statements[0]

    assert type(stmt) == ast.ExpressionStatement

    assert type(stmt.expression) == ast.InfixExpression

    assert stmt.expression.left.value == left

    assert stmt.expression.operator == operator

    assert stmt.expression.right.value == right


@pytest.mark.parametrize(
    "source,expected",
    [
        ("-a * b", "((-a) * b)"),
        ("!-a", "(!(-a))"),
        ("a + b + c", "((a + b) + c)"),
        ("a + b - c", "((a + b) - c)"),
        ("a * b * c", "((a * b) * c)"),
        ("a * b / c", "((a * b) / c)"),
        ("a + b / c", "(a + (b / c))"),
        ("a + b * c + d / e - f", "(((a + (b * c)) + (d / e)) - f)"),
        ("3 + 4; -5 * 5", "(3 + 4)((-5) * 5)"),
        ("5 > 4 == 3 < 4", "((5 > 4) == (3 < 4))"),
        ("5 < 4 != 3 > 4", "((5 < 4) != (3 > 4))"),
        ("true", "true"),
        ("false", "false"),
        ("3 > 5 == true", "((3 > 5) == true)"),
        ("3 < 5 == true", "((3 < 5) == true)"),
        ("1 + (2 + 3) + 4", "((1 + (2 + 3)) + 4)"),
        ("(5 + 5) * 2", "((5 + 5) * 2)"),
        ("a + add(b * c) + d", "((a + add((b * c))) + d)"),
        (
            "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
            "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
        ),
        ("add(a + b + c * d / f + g)", "add((((a + b) + ((c * d) / f)) + g))"),
        ("a * [1, 2, 3, 4][b * c] * d", "((a * ([1, 2, 3, 4][(b * c)])) * d)"),
        (
            "add(a * b[2], b[1], 2 * [1, 2][1])",
            "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))",
        ),
    ],
)
def test_operator_precedence_parsing(source, expected):
    l = Lexer(source)
    p = Parser(l)
    program = p.parse_program()
    assert p.errors == []
    assert str(program) == expected


def test_boolean_expression():
    source = "true;"

    l = Lexer(source)
    p = Parser(l)

    program = p.parse_program()
    assert p.errors == []

    assert len(program.statements) == 1

    stmt = program.statements[0]

    assert type(stmt) == ast.ExpressionStatement

    assert type(stmt.expression) == ast.Boolean

    ident = stmt.expression

    assert ident.value == True
    assert ident.token_literal() == "true"


def test_if_expression():
    source = "if (x < y) { x }"

    l = Lexer(source)
    p = Parser(l)

    program = p.parse_program()
    assert p.errors == []

    assert len(program.statements) == 1

    stmt = program.statements[0]

    assert type(stmt) == ast.ExpressionStatement

    assert type(stmt.expression) == ast.IfExpression

    assert stmt.expression.condition.left.value == "x"

    assert stmt.expression.condition.operator == "<"

    assert stmt.expression.condition.right.value == "y"

    # TODO Finish defining me please

    assert len(stmt.expression.consequence.statements) == 1


def test_function_literal_parsing():

    source = "fn(x, y) { x + y; }"

    l = Lexer(source)
    p = Parser(l)

    program = p.parse_program()
    assert p.errors == []

    assert len(program.statements) == 1

    stmt = program.statements[0]

    assert type(stmt) == ast.ExpressionStatement

    assert type(stmt.expression) == ast.FunctionLiteral

    assert [str(s) for s in stmt.expression.params] == ["x", "y"]

    # TODO finish me off please


@pytest.mark.parametrize(
    "source,expected",
    [
        ("fn() {};", []),
        ("fn(x) {};", ["x"]),
        ("fn(x, y, z) {};", ["x", "y", "z"]),
    ],
)
def test_function_parameter_parsing(source, expected):
    l = Lexer(source)
    p = Parser(l)
    program = p.parse_program()
    assert p.errors == []
    stmt = program.statements[0]
    assert type(stmt) == ast.ExpressionStatement
    assert type(stmt.expression) == ast.FunctionLiteral

    func: ast.FunctionLiteral = stmt.expression

    assert len(func.params) == len(expected)


def test_call_expression_parsing():
    source = "add(1, 2 * 3, 4 + 5);"

    l = Lexer(source)
    p = Parser(l)

    program = p.parse_program()
    assert p.errors == []

    assert len(program.statements) == 1

    stmt = program.statements[0]

    assert isinstance(stmt, ast.ExpressionStatement)

    assert isinstance(stmt.expression, ast.CallExpression)

    assert stmt.expression.function.value == "add"

    assert len(stmt.expression.arguments) == 3

    assert stmt.expression == ast.CallExpression(
        token=Token(tok_type="(", literal="("),
        function=ast.Identifier(
            token=Token(tok_type="IDENT", literal="add"), value="add"
        ),
        arguments=[
            ast.IntegerLiteral(token=Token(tok_type="INT", literal="1"), value=1),
            ast.InfixExpression(
                token=Token(tok_type="*", literal="*"),
                left=ast.IntegerLiteral(
                    token=Token(tok_type="INT", literal="2"), value=2
                ),
                operator="*",
                right=ast.IntegerLiteral(
                    token=Token(tok_type="INT", literal="3"), value=3
                ),
            ),
            ast.InfixExpression(
                token=Token(tok_type="+", literal="+"),
                left=ast.IntegerLiteral(
                    token=Token(tok_type="INT", literal="4"), value=4
                ),
                operator="+",
                right=ast.IntegerLiteral(
                    token=Token(tok_type="INT", literal="5"), value=5
                ),
            ),
        ],
    )

    assert str(stmt.expression) == "add(1, (2 * 3), (4 + 5))"


def test_string_literal_expression():
    source = '"hello world";'
    l = Lexer(source)
    p = Parser(l)
    program = p.parse_program()
    assert p.errors == []
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    assert isinstance(stmt.expression, ast.StringLiteral)
    assert stmt.expression.value == "hello world"


def test_parsing_array_literal():
    source = "[1, 2 * 2, 3 + 3];"
    l = Lexer(source)
    p = Parser(l)
    program = p.parse_program()
    assert p.errors == []
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    array = stmt.expression
    assert isinstance(array, ast.ArrayLiteral)
    assert len(array.elements) == 3
    literal = array.elements[0]
    assert literal.value == 1
    assert literal.token_literal() == "1"


def test_parsing_index_expressions():
    source = "myArray[1 + 1]"
    l = Lexer(source)
    p = Parser(l)
    program = p.parse_program()
    assert p.errors == []
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    expression = stmt.expression
    assert isinstance(expression, ast.IndexExpression)
    left = expression.left
    assert isinstance(left, ast.Identifier)
    assert left.value == "myArray"
    assert left.token_literal() == "myArray"
    check_infix_expression(expression.index, 1, "+", "1")


def check_infix_expression(exp: ast.Node, left: Any, operator: str, right: Any):
    assert isinstance(exp, ast.InfixExpression)
    check_literal_expression(exp.left, left)
    assert exp.operator == operator
    check_literal_expression(exp.right, right)


def check_literal_expression(exp: ast.Node, expected: Any):
    if isinstance(exp, int):
        check_integer_literal(exp, expected)
    elif isinstance(exp, str):
        check_identifier(exp, expected)
    else:
        assert "Type not known"


def check_identifier(exp: ast.Node, value: str):
    assert isinstance(exp, ast.Identifier)
    assert exp.value == value
    assert exp.token_literal() == str(value)


def check_integer_literal(il: ast.Node, val: int):
    assert isinstance(il, ast.IntegerLiteral)
    assert il.value == val
    assert il.token_literal() == str(val)


def test_parsing_hash_literal():
    source = '{"one": 1, "two": 2, "three": 3}'
    l = Lexer(source)
    p = Parser(l)
    program = p.parse_program()
    assert p.errors == []
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    hash_literal = stmt.expression
    assert isinstance(hash_literal, ast.HashLiteral)

    assert len(hash_literal.pairs) == 3

    expected = {"one": 1, "two": 2, "three": 3}

    for key, value in hash_literal.pairs.items():
        assert isinstance(key, ast.StringLiteral)
        check_integer_literal(value, expected[str(key)])


def test_parsing_empty_hash_literal():
    source = "{}"

    l = Lexer(source)
    p = Parser(l)
    program = p.parse_program()
    assert p.errors == []
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    hash_literal = stmt.expression
    assert isinstance(hash_literal, ast.HashLiteral)
    assert len(hash_literal.pairs) == 0


def test_parsing_hash_literal_with_expressions():
    source = '{"one": 0 + 1, "two": 10 - 8, "three": 15 / 5}'
    l = Lexer(source)
    p = Parser(l)
    program = p.parse_program()
    assert p.errors == []
    stmt = program.statements[0]
    assert isinstance(stmt, ast.ExpressionStatement)
    hash_literal = stmt.expression
    assert isinstance(hash_literal, ast.HashLiteral)

    assert len(hash_literal.pairs) == 3

    tests = {
        "one": lambda e: check_infix_expression(e, 0, "+", 1),
        "two": lambda e: check_infix_expression(e, 10, "-", 8),
        "three": lambda e: check_infix_expression(e, 15, "/", 5),
    }

    for key, value in hash_literal.pairs.items():
        assert isinstance(key, ast.StringLiteral)
        test_fn = tests[str(key)]
        test_fn(value)
