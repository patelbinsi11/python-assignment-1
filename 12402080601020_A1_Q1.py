import sys
import heapq
from collections import defaultdict


def parse_input(data):
    try:
        n, k, m = int(data[0]), int(data[1]), int(data[2])
    except (IndexError, ValueError):
        raise ValueError("Header must be: n k m")
    if not (1 <= n <= 100000 and 1 <= k <= 50 and 1 <= m <= 12):
        raise ValueError("n, k or m out of range")
    records, pos = [], 3
    for i in range(n):
        try:
            enr, name = data[pos], data[pos + 1]
            sem, cpi = int(data[pos + 2]), float(data[pos + 3])
            marks = [int(x) for x in data[pos + 4: pos + 4 + m]]
        except (IndexError, ValueError):
            raise ValueError(f"Malformed record #{i + 1}")
        if len(marks) != m or not (1 <= sem <= 8) or not (0.0 <= cpi <= 10.0) \
                or any(not 0 <= x <= 100 for x in marks):
            raise ValueError(f"Invalid values in record #{i + 1}")
        records.append((enr, name, sem, cpi, marks))
        pos += 4 + m
    return n, k, m, records


def analyze(k, m, records):
    by_sem = defaultdict(list)
    best = [(-1, []) for _ in range(m)]
    for enr, _name, sem, cpi, marks in records:
        by_sem[sem].append((-cpi, -sum(marks) / m, enr))
        for j, mk in enumerate(marks):
            if mk > best[j][0]:
                best[j] = (mk, [enr])
            elif mk == best[j][0]:
                best[j][1].append(enr)
    lines = []
    for sem in sorted(by_sem):
        top = heapq.nsmallest(k, by_sem[sem])
        lines.append(f"Semester {sem}: " + " ".join(t[2] for t in top))
    for j in range(m):
        lines.append(f"S{j + 1}: " + " ".join(sorted(best[j][1])))
    return lines


def main():
    try:
        _n, k, m, records = parse_input(sys.stdin.read().split())
    except ValueError as e:
        print("Input error:", e)
        return
    print("\n".join(analyze(k, m, records)))


if __name__ == "__main__":
    main()