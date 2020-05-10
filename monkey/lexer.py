from typing import Optional

import monkey.ast as ast
import monkey.token as token


# [TODO]
# - Would this be possible to do without mutable state,
# - Can we wrap this is a custom generator that consumes a byte at a time (+ 1
# extra byte for peek char)


class Lexer:
    input: str
    position: int
    read_position: int
    ch: Optional[str]

    def __init__(self, input: str) -> None:
        self.input = input
        self.position = 0
        self.read_position = 0
        self.ch = ""
        self.read_char()

    def read_char(self) -> None:
        if self.read_position >= len(self.input):
            self.ch = None
        else:
            self.ch = self.input[self.read_position]
        self.position = self.read_position
        self.read_position += 1

    def peek_char(self) -> Optional[str]:
        if self.read_position >= len(self.input):
            self.ch = None
            return None
        else:
            return self.input[self.read_position]

    def skip_whitespace(self) -> None:
        while self.ch is not None and self.ch.isspace():
            self.read_char()

    def next_token(self) -> token.Token:
        # Consume space characters to advance the lexer
        self.skip_whitespace()

        if self.ch is None:
            return token.Token(token.EOF, "")
        elif self.ch == "[":
            tok = token.Token(token.LBRACKET, self.ch)
            self.read_char()
            return tok
        elif self.ch == "]":
            tok = token.Token(token.RBRACKET, self.ch)
            self.read_char()
            return tok
        elif self.ch == ":":
            tok = token.Token(token.COLON, self.ch)
            self.read_char()
            return tok
        elif self.ch == '"':
            literal = self.read_string()
            self.read_char()
            return token.Token(tok_type=token.STRING, literal=literal)

        # Attempt to lookup common token types
        tok_type = token.token_table.get(self.ch)
        if tok_type is not None:
            tok = token.Token(tok_type, self.ch)

            if self.ch == "=" and self.peek_char() == "=":
                self.read_char()
                tok = token.Token(token.EQ, "==")
            elif self.ch == "!" and self.peek_char() == "=":
                self.read_char()
                tok = token.Token(token.NOT_EQ, "!=")

        else:
            # If token not found
            if self.ch.isalpha():
                literal = self.read_identifier()
                return token.Token(token.lookup_ident(literal), literal)
            elif self.ch.isdigit():
                return token.Token(token.INT, self.read_number())
            else:
                tok = token.Token(token.ILLEGAL, self.ch)

        self.read_char()
        return tok

    def read_string(self) -> str:
        position = self.position + 1
        while True:
            self.read_char()
            if self.ch == '"' or self.ch == 0:
                break
        return self.input[position : self.position]

    def read_number(self) -> str:
        position = self.position
        while self.ch is not None and self.ch.isdigit():
            self.read_char()
        return self.input[position : self.position]

    def read_identifier(self) -> str:
        position = self.position
        while self.ch is not None and self.ch.isalpha():
            self.read_char()
        return self.input[position : self.position]
