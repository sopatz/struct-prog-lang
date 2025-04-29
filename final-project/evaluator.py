# "Resolves" the value of each token

from tokenizer import tokenize
from parser import parse

printed_string = None

def evaluate(ast, environment={}): #environment is optional
    global printed_string
    if ast["tag"] == "program":
        last_value = None
        for statement in ast["statements"]:
            value = evaluate(statement, environment)
            last_value = value
        return last_value
    if ast["tag"] == "block":
        for statement in ast["statements"]:
            _ = evaluate(statement, environment)
    if ast["tag"] == "print":
        value = evaluate(ast["value"], environment)
        s = str(value)
        print(s)
        printed_string = s
        return None #statement does not return a value, an expression does
    if ast["tag"] == "call":
        func_name = ast["name"]
        args = [evaluate(arg, environment) for arg in ast["args"]]
        if func_name == "pow":
            assert len(args) == 2, "pow() takes exactly two arguments"
            return args[0] ** args[1]
        if func_name == "sqrt": #square root
            assert len(args) == 1, "sqrt() takes exactly one argument"
            result = args[0] ** 0.5
            # Round if close to an integer
            if abs(result - round(result)) < 1e-9:
                return round(result)
            return result
        if func_name == "cbrt": #cube root
            assert len(args) == 1, "cbrt() takes exactly one argument"
            result = args[0] ** (1/3)
            # Correct cube root of negative numbers
            if args[0] < 0:
                result = -((-args[0]) ** (1/3))
            # Round if very close to an integer
            if abs(result - round(result)) < 1e-9:
                return round(result)
        if func_name == "root": #any root
            assert len(args) == 2, "root() takes exactly two arguments"
            assert args[1] != 0, "root() with n = 0 is undefined"
            # Handle negative roots (e.g., cube root of -8 = -2)
            if args[0] < 0 and int(args[1]) % 2 == 1:
                result = -((-args[0]) ** (1 / args[1]))
            else:
                result = args[0] ** (1 / args[1])
            # Round if close to an integer
            if abs(result - round(result)) < 1e-9:
                return round(result)
            return result
        if func_name == "ceil":
            assert len(args) == 1, "ceil() takes exactly one argument"
            x = args[0]
            return int(x) if x == int(x) else (int(x) + 1 if x > 0 else int(x))
        if func_name == "floor":
            assert len(args) == 1, "floor() takes exactly one argument"
            x = args[0]
            return int(x) if x >= 0 or x == int(x) else int(x) - 1
        if func_name == "factorial":
            assert len(args) == 1, "factorial() takes exactly two arguments"
            if args[0] < 0:
                return "Factorial is not defined for negative numbers"
            elif args[0] == 0:
                return 1
            else:
                result = 1
                for i in range(1, args[0] + 1):
                    result *= i
                return result
        if func_name == "gcf": #greatest common factor (GCF)
            result = args[0]
            for x in args[1:]:
                if result < x:
                    temp = result
                    result = x
                    x = temp
                while x != 0:
                    temp = x
                    x = result % x
                    result = temp
            return result
        raise Exception(f"Unknown function '{func_name}'")
    if ast["tag"] == "if":
        condition_value = evaluate(ast["condition"], environment)
        if condition_value:
            evaluate(ast["then"], environment) #evaluate then statement if condition is true
        else:
            if ast["else"]: #ast["else"] != None
                evaluate(ast["else"], environment)
        return None
    if ast["tag"] == "while":
        while evaluate(ast["condition"], environment):
            evaluate(ast["do"], environment) #evaluate then statement if condition is true
        return None
    if ast["tag"] == "do_while":
        while True:
            evaluate(ast["body"], environment)
            if not evaluate(ast["condition"], environment):
                break
        return None
    if ast["tag"] == "sopatz":
        environment["_kentid_"] = "sopatz@kent.edu" #insert and set environment variable
        return None
    if ast["tag"] == "assign":
        target = ast["target"]
        assert target["tag"] == "identifier"
        identifier = target["value"]
        assert type(identifier) is str
        value = evaluate(ast["value"], environment)
        environment[identifier] = value
        return value
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
    if ast["tag"] == "negate":
        value = evaluate(ast["value"], environment)
        return -value
    if ast["tag"] == "&&":
        left_value = evaluate(ast["left"], environment)
        right_value = evaluate(ast["right"], environment)
        return left_value and right_value
    if ast["tag"] == "||":
        left_value = evaluate(ast["left"], environment)
        right_value = evaluate(ast["right"], environment)
        return left_value or right_value
    if ast["tag"] == "!":
        value = evaluate(ast["value"], environment)
        return not value
    if ast["tag"] == "<":
        left_value = evaluate(ast["left"], environment)
        right_value = evaluate(ast["right"], environment)
        return left_value < right_value
    if ast["tag"] == ">":
        left_value = evaluate(ast["left"], environment)
        right_value = evaluate(ast["right"], environment)
        return left_value > right_value
    if ast["tag"] == "<=":
        left_value = evaluate(ast["left"], environment)
        right_value = evaluate(ast["right"], environment)
        return left_value <= right_value
    if ast["tag"] == ">=":
        left_value = evaluate(ast["left"], environment)
        right_value = evaluate(ast["right"], environment)
        return left_value >= right_value
    if ast["tag"] == "==":
        left_value = evaluate(ast["left"], environment)
        right_value = evaluate(ast["right"], environment)
        return left_value == right_value
    if ast["tag"] == "!=":
        left_value = evaluate(ast["left"], environment)
        right_value = evaluate(ast["right"], environment)
        return left_value != right_value
    
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
    assert eval("1<2") == True
    assert eval("2<1") == False
    assert eval("2>1") == True
    assert eval("1>2") == False
    assert eval("1<=2") == True
    assert eval("2<=2") == True
    assert eval("2<=1") == False
    assert eval("2>=1") == True
    assert eval("2>=2") == True
    assert eval("1>=2") == False
    assert eval("2==2") == True
    assert eval("1==2") == False
    assert eval("2!=1") == True
    assert eval("1!=1") == False
    assert eval("-1") == -1
    assert eval("-(1)") == -1
    assert eval("!1") == False
    assert eval("!0") == True
    assert eval("0&&1") == False
    assert eval("1&&1") == True
    assert eval("1||1") == True
    assert eval("0||1") == True
    assert eval("0||0") == False

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

def test_evaluate_assignment():
    print("Testing evaluate assignment...")
    env = {'x':14, 'y':5}
    assert eval("x=7", env) == 7
    assert env["x"] == 7

def test_if_statement():
    print("Testing if statement...")
    env = {"x":4,"y":5}
    assert eval("if(1){x=8}",env) == None
    assert env["x"] == 8
    assert eval("if(0){x=5}else{y=9}",env) == None
    assert env["x"] == 8
    assert env["y"] == 9

def test_while_statement():
    print("Testing while statement...")
    env = {"x":4,"y":5}
    assert eval("while(x<6){y=y+1;x=x+1}",env) == None
    assert env["x"] == 6
    assert env["y"] == 7

def test_do_while_loop():
    print("Testing do-while loop...")
    env = {"x": 0}
    eval("do{x = x + 1}while(x < 3)", env)
    assert env["x"] == 3

def test_math_functions():
    print("Testing math functions...")
    assert eval("pow(2, 3)") == 8
    assert eval("sqrt(9)") == 3
    assert eval("cbrt(64)") == 4
    assert eval("cbrt(-64)") == -4
    assert eval("root(625, 4)") == 5
    assert eval("root(-32, 5)") == -2
    assert eval("ceil(3.2)") == 4
    assert eval("floor(3.9)") == 3
    assert eval("ceil(-3.2)") == -3
    assert eval("floor(-3.9)") == -4
    assert eval("factorial(5)") == 120
    assert eval("gcf(24, 12, 18)") == 6

if __name__ == "__main__":
    test_evaluate_number()
    test_evaluate_add()
    test_evaluate_subtract()
    test_evaluate_multiply()
    test_evaluate_divide()
    test_evaluate_expression()
    test_evaluate_print_statement()
    test_evaluate_identifier()
    test_evaluate_assignment()
    test_if_statement()
    test_while_statement()
    test_do_while_loop()
    test_math_functions()
    print("Done testing evaluator.")