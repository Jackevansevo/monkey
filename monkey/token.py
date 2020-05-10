from typing import Dict, NamedTuple

TokenType = str

ILLEGAL: TokenType = "ILLEGAL"
EOF: TokenType = "EOF"

IDENT: TokenType = "IDENT"
INT: TokenType = "INT"


ASSIGN: TokenType = "="
PLUS: TokenType = "+"
MINUS: TokenType = "-"
BANG: TokenType = "!"
ASTERISK: TokenType = "*"
SLASH: TokenType = "/"

COLON = ":"

LT: TokenType = "<"
GT: TokenType = ">"

EQ: TokenType = "=="
NOT_EQ: TokenType = "!="

COMMA: TokenType = ","
SEMICOLON: TokenType = ";"
LPAREN: TokenType = "("
RPAREN: TokenType = ")"
LBRACE: TokenType = "{"
RBRACE: TokenType = "}"
LBRACKET = "["
RBRACKET = "]"

FUNCTION: TokenType = "FUNCTION"
LET: TokenType = "LET"
TRUE: TokenType = "TRUE"
FALSE: TokenType = "FALSE"
IF: TokenType = "IF"
ELSE: TokenType = "ELSE"
STRING = "STRING"
RETURN: TokenType = "RETURN"


class Token(NamedTuple):
    tok_type: TokenType
    literal: str


def lookup_ident(ident: str) -> TokenType:
    return keywords.get(ident, IDENT)


keywords: Dict[str, TokenType] = {
    "fn": FUNCTION,
    "let": LET,
    "true": TRUE,
    "false": FALSE,
    "if": IF,
    "else": ELSE,
    "return": RETURN,
}

token_table: Dict[str, TokenType] = {
    "=": ASSIGN,
    "+": PLUS,
    "-": MINUS,
    "!": BANG,
    "/": SLASH,
    "*": ASTERISK,
    "<": LT,
    ">": GT,
    ";": SEMICOLON,
    ",": COMMA,
    "(": LPAREN,
    ")": RPAREN,
    "{": LBRACE,
    "}": RBRACE,
}
