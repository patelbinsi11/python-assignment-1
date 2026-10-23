import re
import sys
from collections import deque

# Same character 4 or more times in a row = "more than 3"
REPEAT = re.compile(r"(.)\1{3,}")


def build_automaton(words):
    """Build an Aho-Corasick automaton so all banned words
    are searched in one pass over each password."""
    goto, fail, out = [{}], [0], [False]
    for w in words:                      # 1) build the trie
        node = 0
        for ch in w.lower():
            nxt = goto[node].get(ch)
            if nxt is None:
                goto.append({})
                fail.append(0)
                out.append(False)
                nxt = len(goto) - 1
                goto[node][ch] = nxt
            node = nxt
        out[node] = True                 # a banned word ends here
    q = deque(goto[0].values())          # 2) failure links (BFS)
    while q:
        u = q.popleft()
        for ch, v in goto[u].items():
            f = fail[u]
            while f and ch not in goto[f]:
                f = fail[f]
            fail[v] = goto[f].get(ch, 0)
            out[v] = out[v] or out[fail[v]]
            q.append(v)
    return goto, fail, out


def contains_banned(text, automaton):
    goto, fail, out = automaton
    node = 0
    for ch in text.lower():              # ignore case
        while node and ch not in goto[node]:
            node = fail[node]
        node = goto[node].get(ch, 0)
        if out[node]:
            return True
    return False


def classify(pw, automaton):
    if not 6 <= len(pw) <= 12:
        return "WEAK_LENGTH"
    if contains_banned(pw, automaton):
        return "COMPROMISED"
    has_all = (re.search(r"[a-z]", pw) and re.search(r"[A-Z]", pw)
               and re.search(r"\d", pw) and re.search(r"[$#@]", pw))
    if not has_all or REPEAT.search(pw):
        return "WEAK_PATTERN"
    return "STRONG"


def main():
    lines = sys.stdin.read().split("\n")
    try:
        b = int(lines[0])
        banned = [w.strip() for w in lines[1:1 + b] if w.strip()]
        n = int(lines[1 + b])
        passwords = [p.rstrip("\r") for p in lines[2 + b: 2 + b + n]]
        if len(passwords) != n:
            raise ValueError
    except (ValueError, IndexError):
        print("Input error: expected b, b words, n, n passwords")
        return
    automaton = build_automaton(banned)
    for i, pw in enumerate(passwords, 1):
        print(f"{i}: {classify(pw, automaton)}")


if __name__ == "__main__":
    main()