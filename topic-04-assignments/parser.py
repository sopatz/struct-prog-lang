# Builds abstract syntax trees of tokens using nested Python dictionaries 
# (this is a "recursive descent parser")

from tokenizer import tokenize

"""
parser.py -- implement parser for simple expressions

Accept a string of tokens, return an AST expressed as stack of dictionaries
"""
"""
    factor = <number> | <identifier> | "(" expression ")" | "!" expression | "-" expression
    term = factor { "*"|"/" factor }
    arithmetic_expression = term { "+"|"-" term }
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression } ;
    # logical_factor = relational_expression ;
    # logical_term = logical_factor { "&&" logical_factor } ;
    # logical_expression = logical_term { "||" logical_term } ;
    # expression = logical_expression; 
    assignment_statement = expression [ "=" expression ]
    statement = <print> expression | assignment_statement
    program = [ statement { ";" statement } ]
"""

def parse_factor(tokens):
    """
    factor = <number> | <identifier> | "(" expression ")" | "!" expression | "-" expression
    """
    token = tokens[0]
    if token["tag"] == "number":
        return {
            "tag":"number",
            "value":token['value']
        }, tokens[1:]
    if token["tag"] == "identifier":
        return {
            "tag":"identifier",
            "value":token['value']
        }, tokens[1:]
    if token["tag"] == "(":
        ast, tokens = parse_expression(tokens[1:])
        assert tokens[0]["tag"] == ")"
        return ast, tokens[1:]
    if token["tag"] == "!":
        ast, tokens = parse_expression(tokens[1:])
        return {"tag": "!", "value": ast}, tokens
    if token["tag"] == "-":
        ast, tokens = parse_expression(tokens[1:])
        return {"tag": "negate", "value": ast}, tokens
    raise Exception(f"Unexpected token '{token['tag']} at position {token['position']}")

def test_parse_factor():
    """
    factor = <number> | <identifier> | "(" expression ")" | "!" expression | "-" expression
    """
    print("Testing parse factor...")
    for s in ["1", "22", "333"]:
        tokens = tokenize(s)
        ast, tokens = parse_factor(tokens)
        assert ast == {'tag': 'number', 'value': int(s)}
        assert tokens[0]['tag'] == None
    tokens = tokenize("(22)")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': 'number', 'value': 22}
    tokens = tokenize("(2+3)")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': '+', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 3}}
    tokens = tokenize("x")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': 'identifier', 'value': 'x'}
    tokens = tokenize("(x+3)")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': '+', 'left': {'tag': 'identifier', 'value': 'x'}, 'right': {'tag': 'number', 'value': 3}}
    tokens = tokenize("-(x+4)")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': 'negate', 'value': {'tag': '+', 'left': {'tag': 'identifier', 'value': 'x'}, 'right': {'tag': 'number', 'value': 4}}}
    tokens = tokenize("!2")
    ast, tokens = parse_factor(tokens)
    assert ast == {'tag': '!', 'value': {'tag': 'number', 'value': 2}}

def parse_term(tokens):
    """
    term = factor { "*"|"/" factor }
    """
    node, tokens = parse_factor(tokens) # node = part of ast (part of tree)
    while tokens[0]["tag"] in ["*", "/"]:
        tag = tokens[0]["tag"]
        tokens = tokens[1:]
        right_node, tokens = parse_factor(tokens)
        node = {"tag":tag, "left":node, "right":right_node}

    return node, tokens

def test_parse_term():
    """
    term = factor { "*"|"/" factor }
    """
    print("Testing parse term...")
    for s in ["1", "22", "333"]:
        tokens = tokenize(s)
        ast, tokens = parse_term(tokens)
        assert ast == {'tag': 'number', 'value': int(s)}
        assert tokens[0]['tag'] == None
    tokens = tokenize("2*4")
    ast, tokens = parse_term(tokens)
    assert ast == {'tag': '*', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 4}}
    tokens = tokenize("2*4/6")
    ast, tokens = parse_term(tokens)
    assert ast == {'tag': '/', 'left': {'tag': '*', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 4}}, 'right': {'tag': 'number', 'value': 6}}

def parse_expression(tokens):
    return parse_relational_expression(tokens)

def parse_arithmetic_expression(tokens):
    """
    arithmetic_expression = term { "+"|"-" term }
    """
    node, tokens = parse_term(tokens)
    while tokens[0]["tag"] in ["+", "-"]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": right_node}

    return node, tokens


def test_parse_arithmetic_expression():
    """
    arithmetic_expression = term { "+"|"-" term }
    """
    print("Testing parse arithmetic expression...")
    for s in ["1", "22", "333"]:
        tokens = tokenize(s)
        ast, tokens = parse_arithmetic_expression(tokens)
        assert ast == {"tag": "number", "value": int(s)}
        assert tokens[0]["tag"] == None
    tokens = tokenize("2*4")
    ast, tokens = parse_arithmetic_expression(tokens)
    assert ast == {
        "tag": "*",
        "left": {"tag": "number", "value": 2},
        "right": {"tag": "number", "value": 4},
    }
    tokens = tokenize("1+2*4")
    ast, tokens = parse_arithmetic_expression(tokens)
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 1},
        "right": {
            "tag": "*",
            "left": {"tag": "number", "value": 2},
            "right": {"tag": "number", "value": 4},
        },
    }
    tokens = tokenize("1+(2+3)*4")
    ast, tokens = parse_arithmetic_expression(tokens)
    assert ast == {
        "tag": "+",
        "left": {"tag": "number", "value": 1},
        "right": {
            "tag": "*",
            "left": {
                "tag": "+",
                "left": {"tag": "number", "value": 2},
                "right": {"tag": "number", "value": 3},
            },
            "right": {"tag": "number", "value": 4},
        },
    }

def parse_relational_expression(tokens):
    """
    # relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression } ;
    """
    node, tokens = parse_arithmetic_expression(tokens)
    while tokens[0]["tag"] in ["<" , ">" , "<=" , ">=" , "==" , "!="]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_arithmetic_expression(tokens[1:])
        node = {"tag": tag, "left": node, "right": right_node}

    return node, tokens

def test_parse_relational_expression():
    print("Testing parse relational expression...")
    for operator in ["<" , ">" , "<=" , ">=" , "==" , "!="]:
        tokens = tokenize(f"2{operator}4")
        ast, tokens = parse_relational_expression(tokens)
        assert ast == {
            "tag": operator,
            "left": {"tag": "number", "value": 2},
            "right": {"tag": "number", "value": 4},
        }, f"AST = [{ast}]"
    tokens = tokenize("2>4==3")
    ast, tokens = parse_relational_expression(tokens)  
    assert ast=={'tag': '==', 'left': {'tag': '>', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 4}}, 'right': {'tag': 'number', 'value': 3}}

def parse_logical_factor(tokens):
    """
    logical_factor = relational_expression ;
    """
    return parse_relational_expression(tokens)


def test_parse_logical_factor():
    """
    logical_factor = relational_expression ;
    """
    print("Testing parse logical factor...")
    for s in ["1", "2+2", "3<4"]:
        tokens = tokenize(s)
        ast1, tokens1 = parse_logical_factor(tokens)
        ast2, tokens2 = parse_relational_expression(tokens)
        assert ast1 == ast2

def parse_logical_term(tokens):
    node, tokens = parse_logical_factor(tokens)
    while tokens[0]["tag"] == "":
        pass

def test_parse_logical_term():
    pass

def parse_statement(tokens):
    """
    statement = <print> expression | expression
    """
    if tokens[0]["tag"] == "print":
        value_ast, tokens = parse_expression(tokens[1:])
        ast = {
            'tag':'print',
            'value':value_ast
        }
    else:
        ast, tokens = parse_assignment_statement(tokens)
    return ast, tokens

def test_parse_statement():
    """
    statement = <print> expression | expression
    """
    print("Testing parse statement...")
    tokens = tokenize("1+(2+3)*4")
    ast, tokens = parse_statement(tokens)
    assert ast == {'tag': '+', 'left': {'tag': 'number', 'value': 1}, 'right': {'tag': '*', 'left': {'tag': '+', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 3}}, 'right': {'tag': 'number', 'value': 4}}}
    tokens = tokenize("print 1*4")
    ast, tokens = parse_statement(tokens)
    assert ast == {'tag': 'print', 'value': {'tag': '*', 'left': {'tag': 'number', 'value': 1}, 'right': {'tag': 'number', 'value': 4}}}

def parse_assignment_statement(tokens):
    """
    assignment_statement = expression [ "=" expression ]
    """
    target, tokens = parse_expression(tokens)
    if tokens[0]["tag"] == "=":
        tokens =  tokens[1:]
        value, tokens = parse_expression(tokens)
        return {"tag": "assign", "target": target, "value": value}, tokens
    return target, tokens

def test_parse_assignment_statement():
    """
    assignment_statement = expression [ "=" expression ]
    """
    print("Testing parse assignment statement...")
    ast, tokens = parse_assignment_statement(tokenize("i=2"))
    assert ast == {'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'i'}, 'value': {'tag': 'number', 'value': 2}}
    ast, tokens = parse_assignment_statement(tokenize("x=1+(2*3)/4"))
    assert ast == {'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'x'}, 'value': {'tag': '+', 'left': {'tag': 'number', 'value': 1}, 'right': {'tag': '/', 'left': {'tag': '*', 'left': {'tag': 'number', 'value': 2}, 'right': {'tag': 'number', 'value': 3}}, 'right': {'tag': 'number', 'value': 4}}}}
    ast, tokens = parse_assignment_statement(tokenize("2"))
    assert ast == {'tag': 'number', 'value': 2}

def parse_program(tokens):
    """
    program = [ statement { ";" statement } ]
    """
    statements = []
    if tokens[0]["tag"]:
        statement, tokens = parse_statement(tokens)
        statements.append(statement)
        while tokens[0]["tag"] == ";":
            tokens = tokens[1:]
            statement, tokens = parse_statement(tokens)
            statements.append(statement)
    assert (
        tokens[0]["tag"] == None
    ), f"Expected end of input at position {tokens[0]['position']}, got [{tokens[0]}]"
    return {"tag": "program", "statements": statements}, tokens[1:]

def test_parse_program():
    """
    program = [ statement { ";" statement } ]
    """
    print("Testing parse program...")
    ast, tokens = parse_program(tokenize("x=1; y=2"))
    assert ast == {'tag': 'program', 'statements': [{'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'x'}, 'value': {'tag': 'number', 'value': 1}}, {'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'y'}, 'value': {'tag': 'number', 'value': 2}}]}
    ast, tokens = parse_program(tokenize("print 1; print 2"))
    assert ast == {
        "tag": "program",
        "statements": [
            {"tag": "print", "value": {"tag": "number", "value": 1}},
            {"tag": "print", "value": {"tag": "number", "value": 2}},
        ],
    }


def parse(tokens):
    ast, tokens = parse_program(tokens)
    return ast

if __name__ == "__main__":
    test_parse_factor()
    test_parse_term()
    test_parse_arithmetic_expression()
    test_parse_relational_expression()
    test_parse_logical_factor()
    # test_parse_logical_term() #fix this from committed code (AND GRAB EVALUATOR CODE)
    test_parse_statement()
    test_parse_assignment_statement()
    test_parse_program()
    print("Done Testing.")