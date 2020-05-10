from typing import List

import monkey.object as monkey_obj
from monkey.object import Builtin


def _builtin_len(args: List[monkey_obj.Object]) -> monkey_obj.Object:
    if len(args) != 1:
        return monkey_obj.Error(f"wrong number of arguments. got={len(args)}, want=1")
    item = next(iter(args))
    if isinstance(item, monkey_obj.String):
        return monkey_obj.Integer(value=len(item.value))
    elif isinstance(item, monkey_obj.Array):
        return monkey_obj.Integer(value=len(item.elements))
    else:
        return monkey_obj.Error(
            f"argument to `len` not supported, got {item.object_type()}"
        )


def _builtin_first(args: List[monkey_obj.Object]) -> monkey_obj.Object:
    if len(args) != 1:
        return monkey_obj.Error(f"wrong number of arguments. got={len(args)}, want=1")

    item = next(iter(args))

    if not isinstance(item, monkey_obj.Array):
        return monkey_obj.Error(f"argumetn to `first` must be ARRAY, got {type(item)}")

    if len(item.elements) > 0:
        return item.elements[0]

    return monkey_obj.NULL


def _builtin_last(args: List[monkey_obj.Object]) -> monkey_obj.Object:
    if len(args) != 1:
        return monkey_obj.Error(f"wrong number of arguments. got={len(args)}, want=1")

    item = next(iter(args))

    if not isinstance(item, monkey_obj.Array):
        return monkey_obj.Error(f"argumetn to `last` must be ARRAY, got {type(item)}")

    if len(item.elements) > 0:
        return item.elements[-1]

    return monkey_obj.NULL


def _builtin_rest(args: List[monkey_obj.Object]) -> monkey_obj.Object:
    if len(args) != 1:
        return monkey_obj.Error(f"wrong number of arguments. got={len(args)}, want=1")

    item = next(iter(args))

    if not isinstance(item, monkey_obj.Array):
        return monkey_obj.Error(f"argumetn to `rest` must be ARRAY, got {type(item)}")

    if len(item.elements) > 0:
        return monkey_obj.Array(item.elements[1:])

    return monkey_obj.NULL


def _builtin_push(args: List[monkey_obj.Object]) -> monkey_obj.Object:
    if len(args) != 2:
        return monkey_obj.Error(f"wrong number of arguments. got={len(args)}, want=2")

    arr, obj = args

    if not isinstance(arr, monkey_obj.Array):
        return monkey_obj.Error(f"argumetn to `push` must be ARRAY, got {type(arr)}")

    return monkey_obj.Array(arr.elements + [obj])


def _builtin_puts(args: List[monkey_obj.Object]) -> monkey_obj.Object:
    for arg in args:
        print(arg.inspect())
    return monkey_obj.NULL


builtins = {
    "len": Builtin(fn=_builtin_len),
    "first": Builtin(fn=_builtin_first),
    "last": Builtin(fn=_builtin_last),
    "rest": Builtin(fn=_builtin_rest),
    "push": Builtin(fn=_builtin_push),
    "puts": Builtin(fn=_builtin_puts),
}
