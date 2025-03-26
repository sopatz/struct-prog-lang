# Splits code into tokens (gives each character a tag, value, and position)

import re #regular expression library

#Define patterns for tokens
patterns = [
    [r"print", "print"],
    [r"if", "if"],
    [r"else", "else"],
    [r"while", "while"],
    [r"continue", "continue"],
    [r"break", "break"],
    [r"return", "return"],
    [r"assert", "assert"],
    [r"\d*\.\d+|\d+\.\d*|\d+", "number"], #\d = digit, + means one or more, * means 0 or more
    [r"[a-zA-Z_][a-zA-Z0-9_]*", "identifier"], #identifiers (all keywords must be above the identifiers here)
    [r"\+", "+"],
    [r"\-", "-"],
    [r"\*", "*"],
    [r"\/", "/"],
    [r"\(", "("],
    [r"\)", ")"],
    [r"==", "=="],
    [r"!=", "!="],
    [r"<=", "<="],
    [r">=", ">="],
    [r"<", "<"],
    [r">", ">"],
    [r"\=", "="],
    [r"\;", ";"],
    [r"\&\&", "&&"],
    [r"\|\|", "||"],
    [r"\!", "!"],
    [r"\{", "{"],
    [r"\}", "}"],
    [r"\[", "["],
    [r"\]", "]"],
    [r"\.", "."],
    [r"\s+","whitespace"],
    [r".","error"]
]

for pattern in patterns:
    pattern[0] = re.compile(pattern[0])

def tokenize(characters):
    tokens = []
    position = 0
    while position < len(characters):
        for pattern, tag in patterns:
            match = pattern.match(characters, position)
            if match: break
        assert match
        
        # (process errors)
        if tag == "error":
            raise Exception("Syntax error")
        
        token = {
            "tag":tag,
            "position":position,
            "value":match.group(0) #contents of first group that matches this regular expression
        }
        if token["tag"] == "number":
            if "." in token["value"]:
                token["value"] = float(token["value"])
            else:
                token["value"] = int(token["value"])
        if token["tag"] != "whitespace":
            tokens.append(token)
        position = match.end() #get next position
    #append end-of-stream marker
    tokens.append({
        "tag": None,
        "value": None,
        "position": position,
    })
    return tokens

def test_simple_token():
    print("Testing simple token...")
    examples = "+-*/()=;<>{}[]."
    for example in examples:
        t = tokenize(example)[0]
        assert t["tag"] == example #what type of token is it?
        assert t["position"] == 0 #where the token was found (first position in this case)
        assert t["value"] == example #contents of the token
    examples = "==\t!=\t<=\t>=\t&&\t||\t!".split("\t")
    for example in examples:
        t = tokenize(example)[0]
        assert t["tag"] == example
        assert t["position"] == 0
        assert t["value"] == example

def test_number_token():
    print("Testing number token...")
    for s in ["1", "11"]:
        t = tokenize(s)
    assert len(t) == 2
    assert t[0]["tag"] == "number"
    assert t[0]["value"] == int(s)
    for s in ["1.11", "11.23", "11.", ".696969"]:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "number"
        assert t[0]["value"] == float(s)

def test_multiple_tokens():
    print("Testing multiple tokens...")
    tokens = tokenize("1+2")
    assert tokens == [{'tag': 'number', 'position': 0, 'value': 1}, {'tag': '+', 'position': 1, 'value': '+'}, {'tag': 'number', 'position': 2, 'value': 2}, {'tag': None, 'position': 3, 'value': None}]
    # print(tokens) #<- this is how I got the thing in the above line

def test_whitespace():
    print("Testing whitespace...")
    tokens = tokenize("1 + 2")
    assert tokens == [{'tag': 'number', 'position': 0, 'value': 1}, {'tag': '+', 'position': 2, 'value': '+'}, {'tag': 'number', 'position': 4, 'value': 2}, {'tag': None, 'position': 5, 'value': None}]

def test_keywords():
    print("Testing keywords...")
    for keyword in [
        "print", "if", "else", "while", "continue", "break", "return", "assert"
    ]:
        t = tokenize(keyword)
        assert len(t) == 2
        assert t[0]["tag"] == keyword, f"expected {keyword}, got {t[0]}"
        assert t[0]["value"] == keyword

def test_identifier_tokens():
    print("Testing identifier tokens...")
    for s in ["x", "y", "z", "alpha", "beta", "gamma"]:
        t = tokenize(s)
        assert len(t) == 2
        assert t[0]["tag"] == "identifier"
        assert t[0]["value"] == s

def test_error():
    print("Testing error...")
    try:
        t = tokenize("$1+ 2")
        assert False, "Should have raised an error for invalid character"
    except Exception as e:
        assert "Syntax error" in str(e), f"Unexpected exception: {e}"


if __name__ == "__main__":
    test_simple_token()
    test_number_token()
    test_multiple_tokens()
    test_whitespace()
    test_keywords()
    test_identifier_tokens()
    test_error()