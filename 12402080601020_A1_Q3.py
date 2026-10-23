import re
import sys
import threading

# A token is a number, a variable name, or one of ( ) + - *
TOKEN = re.compile(r"\s*(\d+|[A-Za-z_]\w*|[()+\-*])")


class InvalidError(Exception):
    pass


class CycleError(Exception):
    pass


def tokenize(text):
    toks, pos, text = [], 0, text.rstrip()
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m:
            raise InvalidError("bad character")
        toks.append(m.group(1))
        pos = m.end()
    if not toks:
        raise InvalidError("empty expression")
    return toks


class Engine:
    def __init__(self, definitions):
        self.defs = definitions    # variable name -> expression text
        self.memo = {}             # variable name -> already computed value
        self.visiting = set()      # variables currently being evaluated

    def evaluate(self, text):
        toks = tokenize(text)
        value, pos = self.expr(toks, 0)
        if pos != len(toks):
            raise InvalidError("extra tokens")
        return value

    # expr   := term (('+' | '-') term)*
    def expr(self, t, i):
        v, i = self.term(t, i)
        while i < len(t) and t[i] in "+-":
            op = t[i]
            r, i = self.term(t, i + 1)
            v = v + r if op == "+" else v - r
        return v, i

    # term   := factor ('*' factor)*
    def term(self, t, i):
        v, i = self.factor(t, i)
        while i < len(t) and t[i] == "*":
            r, i = self.factor(t, i + 1)
            v *= r
        return v, i

    # factor := number | variable | '(' expr ')'
    def factor(self, t, i):
        if i >= len(t):
            raise InvalidError("unexpected end")
        tok = t[i]
        if tok.isdigit():
            return int(tok), i + 1
        if tok == "(":
            v, i = self.expr(t, i + 1)
            if i >= len(t) or t[i] != ")":
                raise InvalidError("missing )")
            return v, i + 1
        if tok[0].isalpha() or tok[0] == "_":
            return self.variable(tok), i + 1
        raise InvalidError("unexpected token " + tok)

    def variable(self, name):
        if name in self.memo:              # memoization: reuse the answer
            return self.memo[name]
        if name in self.visiting:          # we came back to ourselves
            raise CycleError(name)
        if name not in self.defs:
            raise InvalidError("undefined variable " + name)
        self.visiting.add(name)
        value = self.evaluate(self.defs[name])
        self.visiting.discard(name)
        self.memo[name] = value
        return value


def solve():
    lines = sys.stdin.read().split("\n")
    try:
        v = int(lines[0])
        defs = {}
        for line in lines[1:1 + v]:
            name, expr = line.split("=", 1)
            name = name.strip()
            if not re.fullmatch(r"[A-Za-z_]\w*", name):
                raise ValueError
            defs[name] = expr
        target = lines[1 + v]
    except (ValueError, IndexError):
        print("INVALID")
        return
    try:
        print(Engine(defs).evaluate(target))
    except CycleError:
        print("CYCLE")
    except InvalidError:
        print("INVALID")


if __name__ == "__main__":
    sys.setrecursionlimit(1_000_000)       # allow very long variable chains
    try:
        threading.stack_size(64 * 1024 * 1024)   # 64 MB, accepted on Windows
    except (ValueError, RuntimeError):
        pass                                      # use the default size if refused
    t = threading.Thread(target=solve)
    t.start()
    t.join()