import monkey.ast as ast
import monkey.token as token


def test_string():

    program = ast.Program()
    statements = [
        ast.LetStatement(
            token=token.Token(token.LET, "let"),
            name=ast.Identifier(token=token.Token(token.IDENT, "myVar"), value="myVar"),
            value=ast.Identifier(
                token=token.Token(token.IDENT, "anotherVar"), value="anotherVar"
            ),
        )
    ]
    program.statements = statements
    assert str(program) == "let myVar = anotherVar"
