import heapq
import sys


def main():
    lines = [ln.split() for ln in sys.stdin.read().split("\n") if ln.strip()]
    try:
        n, e = int(lines[0][0]), int(lines[0][1])
        modules = [lines[1 + i][0] for i in range(n)]
        edge_lines = lines[1 + n: 1 + n + e]
    except (IndexError, ValueError):
        print("Input error")
        return

    known = set(modules)
    deps = {m: set() for m in modules}      # module -> modules it imports (set removes duplicates)
    users = {m: [] for m in modules}        # module -> modules that import it
    for parts in edge_lines:
        a, b = parts[0], parts[-1]          # "a b" or "a imports b"
        if a not in known or b not in known:
            print("Ignoring unknown module in edge:", " ".join(parts), file=sys.stderr)
            continue
        if b not in deps[a]:
            deps[a].add(b)
            users[b].append(a)

    indeg = {m: len(deps[m]) for m in modules}          # how many imports each module still waits for
    heap = [m for m in modules if indeg[m] == 0]        # modules that can load now
    heapq.heapify(heap)                                 # smallest name first
    order, done = [], set()
    while heap:
        m = heapq.heappop(heap)
        order.append(m)
        done.add(m)
        for u in users[m]:
            indeg[u] -= 1
            if indeg[u] == 0:
                heapq.heappush(heap, u)

    if len(order) == len(known):
        print(" ".join(order))
        return

    # Some modules never became free, so there is a cycle among them.
    # Each leftover module depends on another leftover one, so following
    # those links must eventually come back to a module we already saw.
    cur = min(m for m in modules if m not in done)
    seen, path = {}, []
    while cur not in seen:
        seen[cur] = len(path)
        path.append(cur)
        cur = min(d for d in deps[cur] if d not in done)
    cycle = path[seen[cur]:] + [cur]
    print("CYCLE")
    print(" -> ".join(cycle))


if __name__ == "__main__":
    main()