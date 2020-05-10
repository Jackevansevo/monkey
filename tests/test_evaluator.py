import pytest
from typing import NamedTuple, Any

from monkey.lexer import Lexer
from monkey.parser import Parser
from monkey.eval import Eval

import monkey.object as monkey_object


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("-50 + 100 + -50", 0),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("20 + 2 * -10", 0),
        ("50 / 2 * 2 + 10", 60),
        ("2 * (5 + 10)", 30),
        ("3 * 3 * 3 + 10", 37),
        ("3 * (3 * 3) + 10", 37),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
    ],
)
def test_eval_integer_expression(test_input, expected):
    evaluated = check_eval(test_input)
    check_integer_object(evaluated, expected)


def check_integer_object(obj: monkey_object.Object, expected: int):
    assert isinstance(obj, monkey_object.Integer)
    assert obj.value == expected


def check_eval(source: str) -> monkey_object.Object:
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    return Eval(program, {})


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("true", True),
        ("false", False),
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1 != 2", True),
        ("true == true", True),
        ("false == false", True),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
    ],
)
def test_eval_boolean_expression(test_input, expected):
    evaluated = check_eval(test_input)
    check_boolean_object(evaluated, expected)


def check_boolean_object(obj: monkey_object.Object, expected: int):
    assert isinstance(obj, monkey_object.Boolean)
    assert obj.value == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
    ],
)
def test_bang_operator(test_input, expected):
    evaluated = check_eval(test_input)
    check_boolean_object(evaluated, expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("if (true) { 10 }", 10),
        ("if (false) { 10 }", None),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 > 2) { 10 }", None),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 < 2) { 10 } else { 20 }", 10),
    ],
)
def test_if_else_expressions(test_input, expected):
    evaluated = check_eval(test_input)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2 * 5; 9;", 10),
        ("9; return 2 * 5; 9;", 10),
        ("if (10 > 1) { if (10 > 1) { return 10; } return 1; }", 10),
    ],
)
def test_return_statements(test_input, expected):
    evaluated = check_eval(test_input)
    check_integer_object(evaluated, expected)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("5 + true;", "type mismatch: INTEGER + BOOLEAN"),
        ("5 + true; 5;", "type mismatch: INTEGER + BOOLEAN"),
        ("-true", "unknown operator: -BOOLEAN"),
        ("true + false;", "unknown operator: BOOLEAN + BOOLEAN"),
        ("5; true + false; 5", "unknown operator: BOOLEAN + BOOLEAN"),
        ("if (10 > 1) { true + false; }", "unknown operator: BOOLEAN + BOOLEAN"),
        (
            "132 if (10 > 1) {if (10 > 1) {return true + false;}return 1;}",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        ("foobar", "identifier not found: foobar"),
        ('"Hello" - "World"', "unknown operator: STRING - STRING"),
    ],
)
def test_error_handling(test_input, expected):
    evaluated = check_eval(test_input)
    assert isinstance(evaluated, monkey_object.Error)
    assert evaluated.msg == expected


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("let a = 5; a;", 5),
        ("let a = 5 * 5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
    ],
)
def test_let_statements(test_input, expected):
    check_integer_object(check_eval(test_input), expected)


def test_function_object():
    source = "fn(x) { x + 2; };"

    evaluated = check_eval(source)

    assert isinstance(evaluated, monkey_object.Function)

    assert len(evaluated.params) == 1

    assert str(evaluated.params[0]) == "x"

    assert str(evaluated.body) == "(x + 2)"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("let identity = fn(x) { x; }; identity(5);", 5),
        ("let identity = fn(x) { return x; }; identity(5);", 5),
        ("let double = fn(x) { x * 2; }; double(5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
        ("fn(x) { x; }(5)", 5),
    ],
)
def test_function_application(test_input, expected):
    check_integer_object(check_eval(test_input), expected)


def test_string_literal():
    source = '"Hello World!"'

    evaluated = check_eval(source)
    assert isinstance(evaluated, monkey_object.String)
    assert evaluated.value == "Hello World!"


def test_string_concatenation():
    source = '"Hello" + " " + "World!"'
    evaluated = check_eval(source)
    assert isinstance(evaluated, monkey_object.String)
    assert evaluated.value == "Hello World!"


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ('len("")', 0),
        ('len("four")', 4),
        ('len("hello world")', 11),
        ("len(1)", "argument to `len` not supported, got INTEGER"),
        ('len("one", "two")', "wrong number of arguments. got=2, want=1"),
    ],
)
def test_builtin_functions(test_input, expected):
    evaluated = check_eval(test_input)
    if type(expected) == int:
        check_integer_object(evaluated, expected)
    elif type(expected) == str:
        assert isinstance(evaluated, monkey_object.Error)
        assert evaluated.msg == expected


def test_array_literals():
    source = "[1, 2 * 2, 3 + 3]"
    evaluated = check_eval(source)
    assert isinstance(evaluated, monkey_object.Array)
    assert len(evaluated.elements) == 3
    check_integer_object(evaluated.elements[0], 1)
    check_integer_object(evaluated.elements[1], 4)
    check_integer_object(evaluated.elements[2], 6)


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (
            "[1, 2, 3][0]",
            1,
        ),
        ("[1, 2, 3][1]", 2),
        ("[1, 2, 3][2]", 3),
        ("let i = 0; [1][i];", 1),
        ("[1, 2, 3][1 + 1];", 3),
        ("let myArray = [1, 2, 3]; myArray[2];", 3),
        ("let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];", 6),
        ("let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]", 2),
        ("[1, 2, 3][3]", None),
        ("[1, 2, 3][-1]", None),
    ],
)
def test_array_index_expressions(test_input, expected):
    evaluated = check_eval(test_input)
    if isinstance(expected, int):
        check_integer_object(evaluated, int(expected))
    else:
        assert evaluated == monkey_object.NULL
