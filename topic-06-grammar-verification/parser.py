# Builds abstract syntax trees of tokens using nested Python dictionaries 
# (this is a "recursive descent parser")

from tokenizer import tokenize

"""
parser.py -- implement parser for simple expressions

EBNF (Extended Backus–Naur Form): Unordered list of rules used to make a formal description of a language (such as our computer programming language)
* Adding numbers to scientific notation (10E3, e.g.): best done with regular expressions rather than BNF's (add 'E' to tokens available)
* Adding tokens to language is regular expression problem, adding logic to these tokens is the job of BNF's

Accept a string of tokens, return an AST expressed as stack of dictionaries
"""
grammar = """
    factor = <number> | <identifier> | "(" expression ")" | "!" expression | "-" expression
    term = factor { "*"|"/" factor }
    arithmetic_expression = term { "+"|"-" term }
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression } ;
    logical_factor = relational_expression ;
    logical_term = logical_factor { "&&" logical_factor } ;
    logical_expression = logical_term { "||" logical_term } ;
    expression = logical_expression; 
    assignment_statement = expression [ "=" expression ]
    statement_block = "{" + statement { ";" statement } + "}"
    print_statement = "print" [ expression ] ;
    if_statement = "if" "(" expression ")" statement_block [ "else" statement_block ]
    while_statement = "while" "(" expression ")" statement_block
    statement = if_statement | while_statement | function_statement | return_statement | print_statement | assignment_statement ;
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
    raise Exception(f"Unexpected token '{token['tag']}' at position {token['position']}")

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
    ast, _ = parse_factor(tokenize("-x"))
    assert ast == {'tag': 'negate', 'value': {'tag': 'identifier', 'value': 'x'}}
    ast, _ = parse_factor(tokenize("-(z/5)"))
    assert ast == {'tag': 'negate', 'value': {'tag': '/', 'left': {'tag': 'identifier', 'value': 'z'}, 'right': {'tag': 'number', 'value': 5}}}

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
    ast, _ = parse_term(tokenize("10/x/5"))
    assert ast == {'tag': '/', 'left': {'tag': '/', 'left': {'tag': 'number', 'value': 10}, 'right': {'tag': 'identifier', 'value': 'x'}}, 'right': {'tag': 'number', 'value': 5}}
    ast, _ = parse_term(tokenize("10/(x/5)"))
    assert ast == {'tag': '/', 'left': {'tag': 'number', 'value': 10}, 'right': {'tag': '/', 'left': {'tag': 'identifier', 'value': 'x'}, 'right': {'tag': 'number', 'value': 5}}}
    ast, _ = parse_term(tokenize("(-z)/5"))
    assert ast == {'tag': '/', 'left': {'tag': 'negate', 'value': {'tag': 'identifier', 'value': 'z'}}, 'right': {'tag': 'number', 'value': 5}}

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

# RELATIONAL EXPRESSIONS

def parse_relational_expression(tokens):
    """
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression } ;
    """
    node, tokens = parse_arithmetic_expression(tokens)
    while tokens[0]["tag"] in ["<" , ">" , "<=" , ">=" , "==" , "!="]:
        tag = tokens[0]["tag"]
        right_node, tokens = parse_arithmetic_expression(tokens[1:])
        node = {"tag": tag, "left": node, "right": right_node}

    return node, tokens

def test_parse_relational_expression():
    """
    relational_expression = arithmetic_expression { ("<" | ">" | "<=" | ">=" | "==" | "!=") arithmetic_expression } ;
    """
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
    assert parse_relational_expression(tokenize("x<y>z"))[0] == {
        "tag": ">",
        "left": {
            "tag": "<",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }

# LOGICAL EXPRESSIONS

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
    assert parse_logical_factor(tokenize("x"))[0] == {"tag": "identifier", "value": "x"}
    assert parse_logical_factor(tokenize("!x"))[0] == {
        "tag": "!",
        "value": {"tag": "identifier", "value": "x"},
    }

def parse_logical_term(tokens):
    """
    logical_term = logical_factor { "&&" logical_factor } ;
    """
    node, tokens = parse_logical_factor(tokens)
    while tokens[0]["tag"] == "&&":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_factor(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens

def test_parse_logical_term():
    """
    logical_term = logical_factor { "&&" logical_factor } ;
    """
    print("Testing parse logical term...")
    assert parse_logical_term(tokenize("x"))[0] == {"tag": "identifier", "value": "x"}
    assert parse_logical_term(tokenize("x&&y"))[0] == {
        "tag": "&&",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_logical_term(tokenize("x&&y&&z"))[0] == {
        "tag": "&&",
        "left": {
            "tag": "&&",
            "left": {"tag": "identifier", "value": "x"},
            "right": {"tag": "identifier", "value": "y"},
        },
        "right": {"tag": "identifier", "value": "z"},
    }

def parse_logical_expression(tokens):
    """
    logical_expression = logical_term { "||" logical_term } ;
    """
    node, tokens = parse_logical_term(tokens)
    while tokens[0]["tag"] == "||":
        tag = tokens[0]["tag"]
        next_node, tokens = parse_logical_term(tokens[1:])
        node = {"tag": tag, "left": node, "right": next_node}
    return node, tokens

def test_parse_logical_expression():
    """
    logical_expression = logical_term { "||" logical_term } ;
    """
    print("Testing parse logical expression...")

    assert parse_logical_expression(tokenize("x"))[0] == {
        "tag": "identifier",
        "value": "x",
    }
    assert parse_logical_expression(tokenize("x||y"))[0] == {
        "tag": "||",
        "left": {"tag": "identifier", "value": "x"},
        "right": {"tag": "identifier", "value": "y"},
    }
    assert parse_logical_expression(tokenize("x||y&&z"))[0] == {
        "tag": "||",
        "left": {"tag": "identifier", "value": "x"},
        "right": {
            "tag": "&&",
            "left": {"tag": "identifier", "value": "y"},
            "right": {"tag": "identifier", "value": "z"},
        },
    }

def parse_expression(tokens):
    """
    expression = logical_expression;
    """
    return parse_logical_expression(tokens)

def test_parse_expression():
    """
    expression = logical_expression;
    """
    print("testing parse_expression...")
    for s in ["1", "1+1", "1 && 1", "1 < 2"]:
        t = tokenize(s)
        assert parse_expression(t) == parse_logical_expression(t)

# STATEMENTS

def parse_statement_block(tokens):
    """
    statement_block = "{" + statement { ";" statement } + "}"
    """
    ast = {"tag": "block", "statements": []} #empty block statement to hold hold one or multiple statements
    assert tokens[0]["tag"] == "{" #check for open bracket at start of block
    tokens = tokens[1:]
    if tokens[0]["tag"] != "}":
        statement, tokens = parse_statement(tokens)
        ast["statements"].append(statement)
    while tokens[0]["tag"] == ";":
        statement, tokens = parse_statement(tokens[1:])
        ast["statements"].append(statement)
    assert tokens[0]["tag"] == "}"
    return ast, tokens[1:] #last token needs consumed

def test_parse_statement_block():
    """
    statement_block = "{" + statement { ";" statement } + "}"
    """
    print("Testing parse statement block...")
    ast = parse_statement_block(tokenize("{}"))[0]
    assert ast == {'tag': 'block', 'statements': []}
    ast = parse_statement_block(tokenize("{i=3}"))[0]
    assert ast == {'tag': 'block', 'statements': [{'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'i'}, 'value': {'tag': 'number', 'value': 3}}]}
    ast = parse_statement_block(tokenize("{i=3; a=17}"))[0]
    assert ast == {'tag': 'block', 'statements': [{'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'i'}, 'value': {'tag': 'number', 'value': 3}}, {'tag': 'assign', 'target': {'tag': 'identifier', 'value': 'a'}, 'value': {'tag': 'number', 'value': 17}}]}

def parse_print_statement(tokens):
    """
    print_statement = "print" [ expression ] ;
    """
    assert tokens[0]["tag"] == "print"
    tokens = tokens[1:]
    if tokens[0]["tag"] in ["}", ";", None]:
        # no expression
        return {"tag": "print", "value": None}, tokens
    else:
        value, tokens = parse_expression(tokens)
        return {"tag": "print", "value": value}, tokens

def test_parse_print_statement():
    """
    print_statement = "print" [ expression ] ;
    """
    print("Testing parse print statement...")
    ast = parse_print_statement(tokenize("print 1"))[0]
    assert ast == {"tag": "print", "value": {"tag": "number", "value": 1}}

def parse_if_statement(tokens):
    """
    if_statement = "if" "(" expression ")" statement_block [ "else" statement_block ]
    """
    assert tokens[0]["tag"] == "if"
    tokens = tokens[1:] #consumue "if" token
    assert tokens[0]["tag"] == "("
    tokens = tokens[1:]
    condition, tokens = parse_expression(tokens)
    assert tokens[0]["tag"] == ")"
    tokens = tokens[1:]
    then_statement, tokens = parse_statement_block(tokens)
    else_statement = None #sends None if we do not have an else statement
    if tokens[0]["tag"] == "else":
        tokens = tokens[1:]
        else_statement, tokens = parse_statement_block(tokens)
    ast = {
        "tag": "if",
        "condition": condition,
        "then": then_statement,
        "else": else_statement
    }
    return ast, tokens

def test_parse_if_statement():
    """
    if_statement = "if" "(" expression ")" statement_block [ "else" statement_block ]
    """
    print("Testing parse if statement...")
    ast, _ = parse_if_statement(tokenize("if(1){print(2)}"))
    assert ast == {'tag': 'if', 
                   'condition': {'tag': 'number', 'value': 1}, 
                   'then': {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 2}}]}, 
                   'else': None}
    ast, _ = parse_if_statement(tokenize("if(1){print(2)}else{print(3)}"))
    assert ast == {'tag': 'if', 
                   'condition': {'tag': 'number', 'value': 1}, 
                   'then': {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 2}}]}, 
                   'else': {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 3}}]}}
    
def parse_while_statement(tokens):
    """
    while_statement = "while" "(" expression ")" statement_block
    """
    assert tokens[0]["tag"] == "while"
    tokens = tokens[1:] #consumue "while" token
    assert tokens[0]["tag"] == "("
    tokens = tokens[1:]
    condition, tokens = parse_expression(tokens)
    assert tokens[0]["tag"] == ")"
    tokens = tokens[1:]
    do_statement, tokens = parse_statement_block(tokens)
    ast = {
        "tag": "while",
        "condition": condition,
        "do": do_statement,
    }
    return ast, tokens

def test_parse_while_statement():
    """
    while_statement = "while" "(" expression ")" statement_block
    """
    print("Testing parse while statement...")
    ast, _ = parse_while_statement(tokenize("while(1){print(2)}"))
    assert ast == {'tag': "while", 
                   'condition': {'tag': 'number', 'value': 1}, 
                   'do': {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 2}}]}}

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

def parse_statement(tokens):
    """
    statement = if_statement | while_statement | function_statement | return_statement | print_statement | assignment_statement ;
    """
    tag = tokens[0]["tag"] # get tag of first token (should be the keyword for the statement)
    # note: none of these consumes a token
    if tag == "{":
        return parse_statement_block(tokens)
    if tag == "if":
        return parse_if_statement(tokens)
    if tag == "while":
        return parse_while_statement(tokens)
    if tag == "sopatz":
        return parse_sopatz_statement(tokens)
    # if tag == "function":
    #     return parse_function_statement(tokens)
    # if tag == "return":
    #     return parse_return_statement(tokens)
    if tag == "print":
        return parse_print_statement(tokens)
    return parse_assignment_statement(tokens)

def parse_sopatz_statement(tokens):
    assert tokens[0]["tag"] == "sopatz"
    tokens = tokens[1:] #consumue "sopatz" token
    return { "tag": "sopatz" }, tokens


def test_parse_statement():
    """
    statement = if_statement | while_statement | function_statement | return_statement | print_statement | assignment_statement ;
    """
    print("Testing parse statement...")

    # statement block
    ast, _ = parse_statement(tokenize("{print 1}"))
    assert ast == {'tag': 'block', 'statements': [{'tag': 'print', 'value': {'tag': 'number', 'value': 1}}]}

    # # if statement
    # assert (
    #     parse_statement(tokenize("if(1){print 1}"))[0]
    #     == parse_if_statement(tokenize("if(1){print 1}"))[0]
    # )
    # # # while statement
    # assert (
    #     parse_statement(tokenize("while(1){print 1}"))[0]
    #     == parse_while_statement(tokenize("while(1){print 1}"))[0]
    # )
    # # return statement
    # assert (
    #     parse_statement(tokenize("return 22"))[0]
    #     == parse_return_statement(tokenize("return 22"))[0]
    # )
    # print statement
    assert (
        parse_statement(tokenize("print 1"))[0]
        == parse_print_statement(tokenize("print 1"))[0]
    )
    # # function_statement (syntactic sugar)
    # assert (
    #     parse_statement(tokenize("function x(y){2}"))[0]
    #     == parse_function_statement(tokenize("function x(y){2}"))[0]
    # )
    # assignment statement
    assert (
        parse_statement(tokenize("x=3"))[0]
        == parse_assignment_statement(tokenize("x=3"))[0]
    )

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

normalized_grammar = "\n".join([line.strip() for line in grammar.splitlines() if line.strip()])

if __name__ == "__main__":
    test_functions = [
        test_parse_factor,
        test_parse_term,
        test_parse_arithmetic_expression,
        test_parse_relational_expression,
        test_parse_logical_factor,
        test_parse_logical_term,
        test_parse_logical_expression,
        test_parse_expression,
        test_parse_statement_block,
        test_parse_print_statement,
        test_parse_if_statement,
        test_parse_while_statement,
        test_parse_assignment_statement,
        test_parse_statement,
        test_parse_program,
    ]

    untested_grammar = normalized_grammar

    # For each test function, verify that:
    # 1. Its docstring rule appears in the normalized grammar.
    # 2. The corresponding parsing function shares the same docstring rule.
    for test_func in test_functions:
        test_rule = test_func.__doc__.strip().splitlines()[0].strip()
        # print("Testing rule from test:", test_rule)
        if test_rule not in untested_grammar:
            raise Exception(f"Rule [{test_rule}] not found in grammar.")
        untested_grammar = untested_grammar.replace(test_rule, "").strip()

        # Determine the corresponding parsing function name (drop the "test_" prefix).
        parsing_func_name = test_func.__name__[5:]
        if parsing_func_name not in globals():
            raise Exception(f"Parsing function {parsing_func_name} not found for test {test_func.__name__}")
        parsing_func = globals()[parsing_func_name]
        if not parsing_func.__doc__:
            raise Exception(f"Parsing function {parsing_func_name} has no docstring.")
        func_rule = parsing_func.__doc__.strip().splitlines()[0].strip()
        if test_rule != func_rule:
            raise Exception(
                f"Mismatch in docstring rules for {parsing_func_name}: "
                f"test rule is [{test_rule}] but function rule is [{func_rule}]."
            )
        # Run the test function.
        test_func()

    if untested_grammar.strip():
        print("Untested grammar rules:")
        print(untested_grammar)
    else:
        print("All grammar rules are covered.")

    print("Done Testing.")