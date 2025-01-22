import re #regular expression library

#Define patterns for tokens
patterns = [
    [r"\d+", "number"], #\d = digit, + means one or more
    [r"\+", "+"],
    [r"\-", "-"],
    [r"\*", "*"],
    [r"\/", "/"],
    [r"\(", "("],
    [r"\)", ")"],
    [r"\s+", "whitespace"],
    [r".", "error"]
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
            "tag": tag,
            "position": position,
            "value": match.group(0) #contents of first group that matches this regular expression
        }
        if token["tag"] == "number":
            token["value"] = int(token["value"])
        if token["tag"] != "whitespace":
            tokens.append(token)
        position = match.end() #get next position
    #append end-of-stream marker
    tokens.append({
        "tag": None,
        "position": position,
        "value": None
    })
    return tokens

def test_simple_token():
    print("test simple token")
    examples = "+-*/()"
    for example in examples:
        t = tokenize(example)[0]
        assert t["tag"] == example #what type of token is it?
        assert t["position"] == 0 #where the token was found (first position in this case)
        assert t["value"] == example #contents of the token

def test_number_token():
    print("test number token")
    for s in ["1", "11"]:
        t = tokenize(s)
    assert len(t) == 2
    assert t[0]["tag"] == "number"
    assert t[0]["value"] == int(s)

def test_multiple_tokens():
    print("test multiple tokens")
    tokens = tokenize("1+2")
    assert tokens == [{'tag': 'number', 'position': 0, 'value': 1}, {'tag': '+', 'position': 1, 'value': '+'}, {'tag': 'number', 'position': 2, 'value': 2}, {'tag': None, 'position': 3, 'value': None}]
    # print(tokens) #<- this is how I got the thing in the above line

def test_whitespace():
    print("test whitespace")
    tokens = tokenize("1 + 2")
    assert tokens == [{'tag': 'number', 'position': 0, 'value': 1}, {'tag': '+', 'position': 2, 'value': '+'}, {'tag': 'number', 'position': 4, 'value': 2}, {'tag': None, 'position': 5, 'value': None}]

def test_error():
    print("test error")
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
    test_error()