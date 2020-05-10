#! /usr/bin/env python

from __future__ import unicode_literals

import os
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style
from pygments.lexers.html import JavascriptLexer

from monkey.eval import Eval
from monkey.lexer import Lexer
from monkey.parser import Parser
import monkey.token as token

# [TODO]
# - Custom Monkey Pygments lexer
# - Custom completion by extending language keywords + current environment
# bindings

monkey_completer = WordCompleter(list(set(token.keywords)))

style = Style.from_dict(
    {
        "completion-menu.completion": "bg:#008888 #ffffff",
        "completion-menu.completion.current": "bg:#00aaaa #000000",
        "scrollbar.background": "bg:#88aaaa",
        "scrollbar.button": "bg:#222222",
    }
)


def main():

    hist_file = Path("~/.monkeyhist").expanduser()

    # Create history file if it doesn't exist already
    if not hist_file.exists():
        hist_file.touch()

    session = PromptSession(
        history=FileHistory(hist_file), completer=monkey_completer, style=style
    )

    env = {}

    while True:
        try:
            scanned = session.prompt(">> ", lexer=PygmentsLexer(JavascriptLexer))
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        else:
            lexer = Lexer(scanned)
            parser = Parser(lexer)
            program = parser.parse_program()
            if parser.errors:
                for error in parser.errors:
                    print(error)
            evaluated = Eval(program, env)
            session.completer = WordCompleter(list(set(token.keywords) | set(env)))
            if evaluated is not None:
                print(evaluated.inspect())

    print("Farewell!")


if __name__ == "__main__":
    main()