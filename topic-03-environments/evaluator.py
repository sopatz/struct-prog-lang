# "Resolves" the value of each token

from tokenizer import tokenize
from parser import parse

printed_string = None

def evaluate(ast, environment={}): #environment is optional
    global printed_string
    if ast["tag"] == "print":
        value = evaluate(ast["value"])
        s = str(value)
        print(s)
        printed_string = s
        return None #statement does not return a value, an expression does
    if ast["tag"] == "number":
        return ast["value"]
    if ast["tag"] == "identifier":
        if ast["value"] in environment:
            return environment[ast["value"]]
        parent_environment = environment
        while "$parent" in parent_environment:
            parent_environment = environment["$parent"]
            if ast["value"] in parent_environment:
                return parent_environment[ast["value"]]
        raise Exception(f"Value [{ast["value"]}] not found in environment. Environment: {environment}")
    if ast["tag"] in ["+", "-", "*", "/"]:
        #each binary operator has a left and right value as sub-trees to evaluate
        left_value = evaluate(ast["left"], environment)
        right_value = evaluate(ast["right"], environment)
        if ast["tag"] == "+":
            return left_value + right_value
        if ast["tag"] == "-":
            return left_value - right_value
        if ast["tag"] == "*":
            return left_value * right_value
        if ast["tag"] == "/":
            return left_value / right_value

def test_evaluate_number():
    print("Testing evaluate number...")
    assert evaluate({"tag":"number","value":4}) == 4

def test_evaluate_add():
    print("Testing evaluate addition...")
    ast = {"tag":"+","left":{"tag":"number", "value":4}, "right":{"tag":"number","value":7}}
    assert evaluate(ast) == 11

def test_evaluate_subtract():
    print("Testing evaluate subtraction...")
    ast = {"tag":"-","left":{"tag":"number", "value":4}, "right":{"tag":"number","value":2}}
    assert evaluate(ast) == 2

def test_evaluate_multiply():
    print("Testing evaluate multiplication...")
    ast = {"tag":"*","left":{"tag":"number", "value":4}, "right":{"tag":"number","value":7}}
    assert evaluate(ast) == 28

def test_evaluate_divide():
    print("Testing evaluate division...")
    ast = {"tag":"/","left":{"tag":"number", "value":8}, "right":{"tag":"number","value":2}}
    assert evaluate(ast) == 4


def eval(s, environment={}):
    tokens = tokenize(s)
    ast = parse(tokens)
    result = evaluate(ast, environment)
    return result

def test_evaluate_expression():
    print("Testing evaluate expression...")
    tokens = tokenize("1+2+4")
    ast = parse(tokens)
    result = evaluate(ast)
    assert result == 7
    assert eval("1+2+4") == 7
    assert eval("1+2*4") == 9
    assert eval("(1+2)*4") == 12
    assert eval("(1.0+2.1)*3") == 9.3

def test_evaluate_print_statement():
    print("Testing print statement...")
    assert eval("print 16") == None
    assert printed_string == "16"
    assert eval("print 3.14159") == None
    assert printed_string == "3.14159"

def test_evaluate_identifier():
    print("Testing evaluate identifier...")
    try:
        assert eval("x+3") == 6
        raise Exception("Error expected for missing value in environment")
    except Exception as e:
        assert "not found" in str(e)
    assert eval("x+3", {"x":3}) == 6
    assert eval("x-y", {'x':14, 'y':5}) == 9
    assert eval("x+y", {'$parent':{'x':4}, 'y':5}) == 9

if __name__ == "__main__":
    test_evaluate_number()
    test_evaluate_add()
    test_evaluate_subtract()
    test_evaluate_multiply()
    test_evaluate_divide()
    test_evaluate_expression()
    test_evaluate_print_statement()
    test_evaluate_identifier()
    print("Done testing evaluator.")