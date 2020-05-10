from collections import ChainMap
from typing import List, NamedTuple

import monkey.ast as ast
import monkey.object as monkey_obj
from monkey.builtins import builtins


def Eval(node: ast.Node, env) -> monkey_obj.Object:

    if isinstance(node, ast.Program):
        return eval_program(node.statements, env)

    elif isinstance(node, ast.HashLiteral):
        return eval_hash_literal(node, env)

    elif isinstance(node, ast.ArrayLiteral):
        elements = [Eval(e, env) for e in node.elements]
        if len(elements) == 1 and isinstance(elements[0], monkey_obj.Error):
            return elements[0]
        return monkey_obj.Array(elements=elements)

    elif isinstance(node, ast.IndexExpression):
        left = Eval(node.left, env)
        if left is not None and isinstance(left, monkey_obj.Error):
            return left

        index = Eval(node.index, env)
        if index is not None and isinstance(index, monkey_obj.Error):
            return index

        return eval_index_expression(left, index)

    elif isinstance(node, ast.StringLiteral):
        return monkey_obj.String(value=node.value)

    elif isinstance(node, ast.CallExpression):
        function = Eval(node.function, env)
        if function is not None and isinstance(function, monkey_obj.Error):
            return function

        args = [Eval(e, env) for e in node.arguments]
        for arg in args:
            if arg is not None and isinstance(function, monkey_obj.Error):
                return arg
        return apply_function(function, args)

    elif isinstance(node, ast.FunctionLiteral):
        params = node.params
        body = node.body
        return monkey_obj.Function(params, env, body)

    elif isinstance(node, ast.BlockStatement):
        return eval_block_statements(node.statements, env)

    elif isinstance(node, ast.IfExpression):
        return eval_if_expression(node, env)

    elif isinstance(node, ast.Identifier):
        return eval_identifier(node, env)

    elif isinstance(node, ast.LetStatement):
        val = Eval(node.value, env)
        if val is not None and isinstance(val, monkey_obj.Error):
            return val
        env[node.name.value] = val
        return monkey_obj.NULL

    elif isinstance(node, ast.ReturnStatement):
        val = Eval(node.value, env)
        if val is not None and isinstance(val, monkey_obj.Error):
            return val
        return monkey_obj.ReturnValue(value=val)

    elif isinstance(node, ast.ExpressionStatement):
        return Eval(node.expression, env)

    elif isinstance(node, ast.Boolean):
        return native_bool_to_boolean_object(node.value)

    elif isinstance(node, ast.IntegerLiteral):
        return monkey_obj.Integer(value=node.value)

    elif isinstance(node, ast.PrefixExpression):
        right = Eval(node.right, env)
        if right is not None and isinstance(right, monkey_obj.Error):
            return val
        return eval_prefix_expression(node.operator, right)

    elif isinstance(node, ast.InfixExpression):
        left = Eval(node.left, env)
        if left is not None and isinstance(left, monkey_obj.Error):
            return left
        right = Eval(node.right, env)
        if right is not None and isinstance(right, monkey_obj.Error):
            return val
        return eval_infix_expression(node.operator, left, right)

    else:
        raise NotImplementedError(str(node), node.token_literal())


def apply_function(
    fn: monkey_obj.Object, args: List[monkey_obj.Object]
) -> monkey_obj.Object:

    if isinstance(fn, monkey_obj.Function):
        func_environment = {
            param.value: args[index] for index, param in enumerate(fn.params)
        }
        evaluated = Eval(fn.body, ChainMap(func_environment, fn.env))
        return unwrap_return_value(evaluated)
    elif isinstance(fn, monkey_obj.Builtin):
        return fn.fn(args)
    else:
        return monkey_obj.Error(f"not a function: {type(fn)}")


def unwrap_return_value(obj: monkey_obj.Object) -> monkey_obj.Object:
    if isinstance(obj, monkey_obj.ReturnValue):
        return obj.value
    return obj


def eval_identifier(node: ast.Identifier, env):
    val = env.get(node.value)
    if val is not None:
        return val

    builtin = builtins.get(node.value)
    if builtin is not None:
        return builtin

    return monkey_obj.Error(f"identifier not found: {node.value}")


def native_bool_to_boolean_object(value: bool) -> monkey_obj.Boolean:
    return monkey_obj.TRUE if value else monkey_obj.FALSE


def eval_program(stmts: List[ast.Node], env) -> monkey_obj.Object:
    for stmt in stmts:
        result = Eval(stmt, env)
        # If the statement was a return then exit early
        if isinstance(result, monkey_obj.ReturnValue):
            return result.value
        elif isinstance(result, monkey_obj.Error):
            return result
    return result


def eval_block_statements(stmts, env) -> monkey_obj.Object:
    for stmt in stmts:
        result = Eval(stmt, env)
        # If the statement was a return then exit early
        if result is not None and (
            isinstance(result, monkey_obj.ReturnValue)
            or isinstance(result, monkey_obj.Error)
        ):
            return result
    return result


def eval_prefix_expression(operator: str, rhs=monkey_obj.Object) -> monkey_obj.Object:
    if operator == "!":
        return eval_bang_operator(rhs)
    elif operator == "-":
        return eval_minus_prefix_operator(rhs)
    else:
        return monkey_obj.Error(f"unknown operator: {operator}{rhs.object_type()}")


def eval_bang_operator(rhs: monkey_obj.Object) -> monkey_obj.Object:
    if rhs is monkey_obj.TRUE:
        return monkey_obj.FALSE
    elif rhs is monkey_obj.FALSE:
        return monkey_obj.TRUE
    elif rhs is monkey_obj.NULL:
        return monkey_obj.TRUE
    else:
        return monkey_obj.FALSE


def eval_minus_prefix_operator(rhs: monkey_obj.Object) -> monkey_obj.Object:
    if not isinstance(rhs, monkey_obj.Integer):
        return monkey_obj.Error(f"unknown operator: -{rhs.object_type()}")
    return monkey_obj.Integer(value=-(rhs.value))


def eval_infix_expression(
    operator: str, lhs: monkey_obj.Object, rhs: monkey_obj.Object
) -> monkey_obj.Object:
    if isinstance(lhs, monkey_obj.Integer) and isinstance(rhs, monkey_obj.Integer):
        return eval_integer_infix_expression(operator, lhs, rhs)
    elif type(lhs) != type(rhs):
        return monkey_obj.Error(
            f"type mismatch: {lhs.object_type()} {operator} {rhs.object_type()}"
        )

    elif isinstance(lhs, monkey_obj.String) and isinstance(rhs, monkey_obj.String):
        if operator != "+":
            return monkey_obj.Error(
                f"unknown operator: {lhs.object_type()} {operator} {rhs.object_type()}"
            )
        return monkey_obj.String(value=lhs.value + rhs.value)

    elif operator == "==":
        return native_bool_to_boolean_object(lhs == rhs)
    elif operator == "!=":
        return native_bool_to_boolean_object(lhs != rhs)
    return monkey_obj.Error(
        f"unknown operator: {lhs.object_type()} {operator} {rhs.object_type()}"
    )


def eval_integer_infix_expression(
    operator: str, lhs: monkey_obj.Integer, rhs: monkey_obj.Integer
) -> monkey_obj.Object:
    if operator == "+":
        return monkey_obj.Integer(value=lhs.value + rhs.value)
    elif operator == "-":
        return monkey_obj.Integer(value=lhs.value - rhs.value)
    elif operator == "*":
        return monkey_obj.Integer(value=lhs.value * rhs.value)
    elif operator == "/":
        return monkey_obj.Integer(value=lhs.value // rhs.value)
    elif operator == "<":
        return native_bool_to_boolean_object(lhs.value < rhs.value)
    elif operator == ">":
        return native_bool_to_boolean_object(lhs.value > rhs.value)
    elif operator == "==":
        return native_bool_to_boolean_object(lhs.value == rhs.value)
    elif operator == "!=":
        return native_bool_to_boolean_object(lhs.value != rhs.value)
    else:
        return monkey_obj.Error(
            f"unknown operator: {lhs.object_type()} {operator} {rhs.object_type()}"
        )


def eval_index_expression(
    left: monkey_obj.Object, index: monkey_obj.Object
) -> monkey_obj.Object:
    if isinstance(left, monkey_obj.Array) and isinstance(index, monkey_obj.Integer):
        return eval_array_index_expression(left, index)

    elif isinstance(left, monkey_obj.Hash):
        return eval_hash_index_expression(left, index)
    else:
        return monkey_obj.Error(f"index operator not supported: {type(left)}")


def eval_array_index_expression(
    array_obj: monkey_obj.Array, index_obj: monkey_obj.Integer
) -> monkey_obj.Object:
    max_index = len(array_obj.elements) - 1
    if index_obj.value < 0 or index_obj.value > max_index:
        return monkey_obj.NULL
    return array_obj.elements[index_obj.value]


def eval_hash_index_expression(
    hash: monkey_obj.Hash, index_obj: monkey_obj.Object
) -> monkey_obj.Object:
    pair = hash.pairs.get(index_obj.value)
    if pair is None:
        return monkey_obj.NULL
    return pair


def eval_if_expression(if_exp: ast.IfExpression, env) -> monkey_obj.Object:
    condition = Eval(if_exp.condition, env)
    if condition:
        if condition is not None and isinstance(condition, monkey_obj.Error):
            return condition
        return Eval(if_exp.consequence, env)
    elif if_exp.alternative is not None:
        return Eval(if_exp.alternative, env)
    else:
        return monkey_obj.NULL


def eval_hash_literal(node: ast.HashLiteral, env) -> monkey_obj.Object:
    pairs = {}
    for key, val in node.pairs.items():
        key = Eval(key, env)
        if key is not None and isinstance(key, monkey_obj.Error):
            return key
        value = Eval(val, env)
        if value is not None and isinstance(key, monkey_obj.Error):
            return value

        pairs[key.value] = value
    return monkey_obj.Hash(pairs=pairs)
