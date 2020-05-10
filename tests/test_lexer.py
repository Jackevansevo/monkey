from typing import NamedTuple

import monkey.token as token
from monkey.lexer import Lexer


def test_next_token():
    source = """
    let five = 5;
    let ten = 10;

    let add = fn(x, y) {
      x + y;
    };

    let result = add(five, ten);
    !-/*5;
    5 < 10 > 5;

    if (5 < 10) {
       return true;
    } else { 
       return false;
    } 

    10 == 10;
    10 != 9;
    "foobar"
    "foo bar"
    [1, 2];
    {"foo": "bar"}
    """

    class TokenTest(NamedTuple):
        expected_type: token.TokenType
        expected_literal: str

    tests = [
        TokenTest(token.LET, "let"),
        TokenTest(token.IDENT, "five"),
        TokenTest(token.ASSIGN, "="),
        TokenTest(token.INT, "5"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.LET, "let"),
        TokenTest(token.IDENT, "ten"),
        TokenTest(token.ASSIGN, "="),
        TokenTest(token.INT, "10"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.LET, "let"),
        TokenTest(token.IDENT, "add"),
        TokenTest(token.ASSIGN, "="),
        TokenTest(token.FUNCTION, "fn"),
        TokenTest(token.LPAREN, "("),
        TokenTest(token.IDENT, "x"),
        TokenTest(token.COMMA, ","),
        TokenTest(token.IDENT, "y"),
        TokenTest(token.RPAREN, ")"),
        TokenTest(token.LBRACE, "{"),
        TokenTest(token.IDENT, "x"),
        TokenTest(token.PLUS, "+"),
        TokenTest(token.IDENT, "y"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.RBRACE, "}"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.LET, "let"),
        TokenTest(token.IDENT, "result"),
        TokenTest(token.ASSIGN, "="),
        TokenTest(token.IDENT, "add"),
        TokenTest(token.LPAREN, "("),
        TokenTest(token.IDENT, "five"),
        TokenTest(token.COMMA, ","),
        TokenTest(token.IDENT, "ten"),
        TokenTest(token.RPAREN, ")"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.BANG, "!"),
        TokenTest(token.MINUS, "-"),
        TokenTest(token.SLASH, "/"),
        TokenTest(token.ASTERISK, "*"),
        TokenTest(token.INT, "5"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.INT, "5"),
        TokenTest(token.LT, "<"),
        TokenTest(token.INT, "10"),
        TokenTest(token.GT, ">"),
        TokenTest(token.INT, "5"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.IF, "if"),
        TokenTest(token.LPAREN, "("),
        TokenTest(token.INT, "5"),
        TokenTest(token.LT, "<"),
        TokenTest(token.INT, "10"),
        TokenTest(token.RPAREN, ")"),
        TokenTest(token.LBRACE, "{"),
        TokenTest(token.RETURN, "return"),
        TokenTest(token.TRUE, "true"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.RBRACE, "}"),
        TokenTest(token.ELSE, "else"),
        TokenTest(token.LBRACE, "{"),
        TokenTest(token.RETURN, "return"),
        TokenTest(token.FALSE, "false"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.RBRACE, "}"),
        TokenTest(token.INT, "10"),
        TokenTest(token.EQ, "=="),
        TokenTest(token.INT, "10"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.INT, "10"),
        TokenTest(token.NOT_EQ, "!="),
        TokenTest(token.INT, "9"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.STRING, "foobar"),
        TokenTest(token.STRING, "foo bar"),
        TokenTest(token.LBRACKET, "["),
        TokenTest(token.INT, "1"),
        TokenTest(token.COMMA, ","),
        TokenTest(token.INT, "2"),
        TokenTest(token.RBRACKET, "]"),
        TokenTest(token.SEMICOLON, ";"),
        TokenTest(token.LBRACE, "{"),
        TokenTest(token.STRING, "foo"),
        TokenTest(token.COLON, ":"),
        TokenTest(token.STRING, "bar"),
        TokenTest(token.RBRACE, "}"),
        TokenTest(token.EOF, ""),
    ]

    l = Lexer(source)

    for test in tests:
        tok = l.next_token()
        assert tok.tok_type == test.expected_type
