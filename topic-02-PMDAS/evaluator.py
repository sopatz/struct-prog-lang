from tokenizer import tokenize
from parser import parse

def evaluate(ast):
    if ast["tag"] == "number":
        return ast["value"]
    if ast["tag"] in ["+", "-", "*", "/"]:
        #each binary operator has a left and right value as sub-trees to evaluate
        left_value = evaluate(ast["left"])
        right_value = evaluate(ast["right"])
        if ast["tag"] == "+":
            return left_value + right_value
        if ast["tag"] == "-":
            return left_value - right_value
        if ast["tag"] == "*":
            return left_value * right_value
        if ast["tag"] == "/":
            return left_value / right_value

def test_evaluate_number():
    print("testing evaluate number")
    assert evaluate({"tag":"number","value":4}) == 4

def test_evaluate_add():
    print("testing evaluate addition")
    ast = {"tag":"+","left":{"tag":"number", "value":4}, "right":{"tag":"number","value":7}}
    assert evaluate(ast) == 11

def test_evaluate_subtract():
    print("testing evaluate subtraction")
    ast = {"tag":"-","left":{"tag":"number", "value":4}, "right":{"tag":"number","value":2}}
    assert evaluate(ast) == 2

def test_evaluate_multiply():
    print("testing evaluate multiplication")
    ast = {"tag":"*","left":{"tag":"number", "value":4}, "right":{"tag":"number","value":7}}
    assert evaluate(ast) == 28

def test_evaluate_divide():
    print("testing evaluate division")
    ast = {"tag":"/","left":{"tag":"number", "value":8}, "right":{"tag":"number","value":2}}
    assert evaluate(ast) == 4

def eval(s):
    tokens = tokenize(s)
    ast = parse(tokens)
    result = evaluate(ast)
    return result

def test_evaluate_expression():
    print("testing evaluate expression")
    tokens = tokenize("1+2+4")
    ast = parse(tokens)
    result = evaluate(ast)
    assert result == 7
    assert eval("1+2+4") == 7
    assert eval("1+2*4") == 9
    assert eval("(1+2)*4") == 12

if __name__ == "__main__":
    test_evaluate_number()
    test_evaluate_add()
    test_evaluate_subtract()
    test_evaluate_multiply()
    test_evaluate_divide()
    test_evaluate_expression()
    print("Done testing evaluator.")