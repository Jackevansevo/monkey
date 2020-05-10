from enum import Enum, auto
from typing import Callable, List, Dict, Optional

import monkey.token as token
from monkey.lexer import Lexer
import monkey.ast as ast


class ParseException(Exception):
    pass


class NoPrefixParseMethodException(ParseException):
    def __init__(self, expression):
        self.expression = expression


prefixParseFn = Callable[[], ast.Node]
infixParseFn = Callable[[ast.Node], ast.Node]


class OperatorPrecedence(Enum):
    LOWEST = auto()
    EQUALS = auto()
    LESSGREATER = auto()
    SUM = auto()
    PRODUCT = auto()
    PREFIX = auto()
    CALL = auto()
    INDEX = auto()


precedences = {
    token.EQ: OperatorPrecedence.EQUALS,
    token.NOT_EQ: OperatorPrecedence.EQUALS,
    token.LT: OperatorPrecedence.LESSGREATER,
    token.GT: OperatorPrecedence.LESSGREATER,
    token.PLUS: OperatorPrecedence.SUM,
    token.MINUS: OperatorPrecedence.SUM,
    token.SLASH: OperatorPrecedence.PRODUCT,
    token.ASTERISK: OperatorPrecedence.PRODUCT,
    token.LPAREN: OperatorPrecedence.CALL,
    token.LBRACKET: OperatorPrecedence.INDEX,
}


class Parser:

    prefix_parse_fns: Dict[token.TokenType, prefixParseFn]
    infix_parse_fns: Dict[token.TokenType, infixParseFn]

    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.cur_token: token.Token = None
        self.peek_token: token.Token = None
        self.next_token()
        self.next_token()
        self.errors: List[str] = []
        self.prefix_parse_fns = {
            token.LBRACE: self.parse_hash_literal,
            token.STRING: self.parse_string_literal,
            token.IDENT: self.parse_identifier,
            token.INT: self.parse_integer_literal,
            token.BANG: self.parse_prefix_expression,
            token.MINUS: self.parse_prefix_expression,
            token.TRUE: self.parse_boolean,
            token.FALSE: self.parse_boolean,
            token.LPAREN: self.parse_group_expression,
            token.IF: self.parse_if_expression,
            token.FUNCTION: self.parse_function_literal,
            token.LBRACKET: self.parse_array_literal,
        }
        self.infix_parse_fns = {
            token.PLUS: self.parse_infix_expression,
            token.MINUS: self.parse_infix_expression,
            token.SLASH: self.parse_infix_expression,
            token.ASTERISK: self.parse_infix_expression,
            token.EQ: self.parse_infix_expression,
            token.NOT_EQ: self.parse_infix_expression,
            token.LT: self.parse_infix_expression,
            token.GT: self.parse_infix_expression,
            token.LPAREN: self.parse_call_expression,
            token.LBRACKET: self.parse_index_expression,
        }

    def next_token(self) -> None:
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def peek_error(self, t):
        self.errors.append(
            f'expected next token to be "{t}" got "{self.peek_token.tok_type}" instead'
        )

    def cur_token_is(self, t: token.TokenType) -> bool:
        return self.cur_token.tok_type == t

    def peek_token_is(self, t: token.TokenType) -> bool:
        return self.peek_token.tok_type == t

    def expect_peek(self, t: token.TokenType) -> bool:
        if self.peek_token_is(t):
            self.next_token()
            return True
        else:
            self.peek_error(t)
            return False

    def parse_program(self) -> ast.Node:
        program = ast.Program()

        # Continue until EOF
        while not self.cur_token_is(token.EOF):

            # Try and parse a statement
            stmt = self.parse_statement()
            if stmt is not None:
                program.statements.append(stmt)

            # Advance the parser
            self.next_token()

        # Return the 'parsed' program
        return program

    def parse_statement(self) -> Optional[ast.Node]:
        if self.cur_token.tok_type == token.LET:
            return self.parse_let_statement()
        elif self.cur_token.tok_type == token.RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self) -> Optional[ast.LetStatement]:
        stmt_token = self.cur_token

        if not self.expect_peek(token.IDENT):
            return None

        name = ast.Identifier(token=self.cur_token, value=self.cur_token.literal)

        if not self.expect_peek(token.ASSIGN):
            return None

        self.next_token()

        value = self.parse_expression(OperatorPrecedence.LOWEST)

        if self.peek_token_is(token.SEMICOLON):
            self.next_token()

        return ast.LetStatement(token=stmt_token, name=name, value=value)

    def parse_return_statement(self):
        stmt_token = self.cur_token

        self.next_token()
        return_value = self.parse_expression(OperatorPrecedence.LOWEST)

        if self.peek_token_is(token.SEMICOLON):
            self.next_token()

        return ast.ReturnStatement(token=stmt_token, value=return_value)

    def parse_expression_statement(self):
        stmt_token = self.cur_token
        expression = self.parse_expression(OperatorPrecedence.LOWEST)

        if self.peek_token_is(token.SEMICOLON):
            self.next_token()

        return ast.ExpressionStatement(token=stmt_token, expression=expression)

    def parse_expression(self, precedence: OperatorPrecedence) -> ast.Node:
        prefix_fn = self.prefix_parse_fns.get(self.cur_token.tok_type)
        if prefix_fn is None:
            raise NoPrefixParseMethodException(
                f'no prefix parse function for "{self.cur_token.tok_type}" found'
            )
        left_exp = prefix_fn()

        while (
            not self.peek_token_is(token.SEMICOLON)
            and precedence.value < self.peek_precedence().value
        ):
            infix = self.infix_parse_fns.get(self.peek_token.tok_type)
            if infix is None:
                return left_exp
            self.next_token()
            left_exp = infix(left_exp)

        return left_exp

    def parse_string_literal(self) -> ast.Node:
        return ast.StringLiteral(token=self.cur_token, value=self.cur_token.literal)

    def parse_identifier(self) -> ast.Node:
        return ast.Identifier(token=self.cur_token, value=self.cur_token.literal)

    def parse_integer_literal(self) -> ast.Node:
        return ast.IntegerLiteral(
            token=self.cur_token, value=int(self.cur_token.literal)
        )

    def parse_boolean(self) -> ast.Node:
        return ast.Boolean(token=self.cur_token, value=self.cur_token_is(token.TRUE))

    def parse_group_expression(self) -> ast.Node:
        self.next_token()

        exp = self.parse_expression(OperatorPrecedence.LOWEST)

        if not self.expect_peek(token.RPAREN):
            return None

        return exp

    def parse_if_expression(self) -> ast.Node:
        expression_token = self.cur_token

        if not self.expect_peek(token.LPAREN):
            return None

        self.next_token()
        condition = self.parse_expression(OperatorPrecedence.LOWEST)

        if not self.expect_peek(token.RPAREN):
            return None

        if not self.expect_peek(token.LBRACE):
            return None

        consequence = self.parse_block_statement()

        alternative = None

        if self.peek_token_is(token.ELSE):
            self.next_token()

            if not self.expect_peek(token.LBRACE):
                return None

            alternative = self.parse_block_statement()

        return ast.IfExpression(
            token=expression_token,
            condition=condition,
            consequence=consequence,
            alternative=alternative,
        )

    def parse_function_literal(self) -> ast.FunctionLiteral:
        tok = self.cur_token

        if not self.expect_peek(token.LPAREN):
            return None

        params = self.parse_function_parameters()

        if not self.expect_peek(token.LBRACE):
            return None

        body = self.parse_block_statement()

        return ast.FunctionLiteral(token=tok, params=params, body=body)

    def parse_array_literal(self) -> ast.ArrayLiteral:
        tok = self.cur_token
        return ast.ArrayLiteral(
            token=tok, elements=self.parse_expression_list(token.RBRACKET)
        )

    def parse_expression_list(self, end: token.TokenType) -> List[ast.Node]:
        if self.peek_token_is(end):
            self.next_token()
            return []

        self.next_token()
        expressions = [self.parse_expression(OperatorPrecedence.LOWEST)]

        while self.peek_token_is(token.COMMA):
            self.next_token()
            self.next_token()
            expressions.append(self.parse_expression(OperatorPrecedence.LOWEST))

        if not self.expect_peek(end):
            return []

        return expressions

    def parse_function_parameters(self) -> List[ast.Identifier]:
        identifiers: List[ast.Identifier] = []

        if self.peek_token_is(token.RPAREN):
            self.next_token()
            return identifiers

        self.next_token()

        ident = ast.Identifier(token=self.cur_token, value=self.cur_token.literal)
        identifiers.append(ident)

        while self.peek_token_is(token.COMMA):
            self.next_token()
            self.next_token()
            ident = ast.Identifier(token=self.cur_token, value=self.cur_token.literal)
            identifiers.append(ident)

        if not self.expect_peek(token.RPAREN):
            return None

        return identifiers

    def parse_block_statement(self) -> ast.BlockStatement:
        block = ast.BlockStatement(token=self.cur_token, statements=[])

        self.next_token()

        while not self.cur_token_is(token.RBRACE) and not self.cur_token_is(token.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                block.statements.append(stmt)
            self.next_token()

        return block

    def parse_prefix_expression(self) -> ast.Node:
        expression = ast.PrefixExpression(
            token=self.cur_token, operator=self.cur_token.literal, right=None
        )
        self.next_token()
        expression.right = self.parse_expression(OperatorPrecedence.PREFIX)
        return expression

    def parse_infix_expression(self, left: ast.Node) -> ast.Node:
        expression = ast.InfixExpression(
            token=self.cur_token, operator=self.cur_token.literal, left=left, right=None
        )
        precedence = self.cur_precedence()
        self.next_token()
        expression.right = self.parse_expression(precedence)
        return expression

    def parse_index_expression(self, left: ast.Node) -> ast.Node:
        cur_token = self.cur_token
        self.next_token()
        index = self.parse_expression(OperatorPrecedence.LOWEST)
        if not self.expect_peek(token.RBRACKET):
            return None
        return ast.IndexExpression(token=cur_token, left=left, index=index)

    def parse_call_expression(self, left: ast.Node) -> ast.Node:
        cur_token = self.cur_token
        return ast.CallExpression(
            token=cur_token,
            function=left,
            arguments=self.parse_expression_list(token.RPAREN),
        )

    def peek_precedence(self) -> OperatorPrecedence:
        return precedences.get(self.peek_token.tok_type, OperatorPrecedence.LOWEST)

    def cur_precedence(self) -> OperatorPrecedence:
        return precedences.get(self.cur_token.tok_type, OperatorPrecedence.LOWEST)

    def parse_hash_literal(self) -> ast.Node:
        hash_literal = ast.HashLiteral(token=self.cur_token, pairs={})

        while not self.peek_token_is(token.RBRACE):
            self.next_token()
            key = self.parse_expression(OperatorPrecedence.LOWEST)
            if not self.expect_peek(token.COLON):
                return None
            self.next_token()
            value = self.parse_expression(OperatorPrecedence.LOWEST)
            hash_literal.pairs[key] = value

            if not self.peek_token_is(token.RBRACE) and not self.expect_peek(
                token.COMMA
            ):
                return None

        if not self.expect_peek(token.RBRACE):
            return None

        return hash_literal
