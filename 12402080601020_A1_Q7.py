import sys


class FormulaError(Exception):
    pass


class InvalidFormatError(FormulaError):
    pass


class UnknownVariableError(FormulaError):
    pass


class DivisionByZeroError(FormulaError):
    pass


class UnsupportedOperatorError(FormulaError):
    pass


OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "%": lambda a, b: a % b,
}


def to_number(token, variables):
    """Turn an operand (integer, decimal or variable name) into a number."""
    for cast in (int, float):
        try:
            return cast(token)
        except ValueError:
            pass
    if token.isidentifier():
        if token not in variables:
            raise UnknownVariableError(f"variable '{token}' is not defined")
        return variables[token]
    raise InvalidFormatError(f"'{token}' is not a number or variable")


def compute(tokens, variables):
    if len(tokens) == 1:
        return to_number(tokens[0], variables)
    if len(tokens) != 3:
        raise InvalidFormatError("expected: operand operator operand")
    left, op, right = tokens
    a, b = to_number(left, variables), to_number(right, variables)
    if op not in OPS:
        raise UnsupportedOperatorError(f"operator '{op}' is not supported")
    if op in "/%" and b == 0:
        raise DivisionByZeroError("division by zero")
    result = OPS[op](a, b)
    assert isinstance(result, (int, float)), "result must be numeric"
    return result


def process(line, variables):
    tokens = line.split()
    if not tokens:
        raise InvalidFormatError("empty line")
    if len(tokens) >= 2 and tokens[1] == "=":          # assignment like: x = 10
        if not tokens[0].isidentifier():
            raise InvalidFormatError("invalid variable name")
        variables[tokens[0]] = compute(tokens[2:], variables)
        return None
    return compute(tokens, variables)


def main():
    variables = {}
    for raw in sys.stdin:
        line = raw.strip()
        if line.lower() == "quit":
            break
        try:
            result = process(line, variables)
            if result is not None:
                print(result)
        except FormulaError as e:
            print(f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()