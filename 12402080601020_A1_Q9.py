import heapq
import sys
import threading


class Scheduler:
    """Keeps track of which worker is free and when.
    The lock makes worker assignment thread-safe."""

    def __init__(self, workers):
        self._lock = threading.Lock()
        self._free = [(0, w) for w in range(1, workers + 1)]   # (free_time, worker_id)
        heapq.heapify(self._free)

    def acquire_worker(self):
        with self._lock:
            return heapq.heappop(self._free)          # earliest free worker

    def release_worker(self, finish_time, worker_id):
        with self._lock:
            heapq.heappush(self._free, (finish_time, worker_id))


def main():
    lines = [ln.split() for ln in sys.stdin.read().split("\n") if ln.strip()]
    try:
        w, n = int(lines[0][0]), int(lines[0][1])
        jobs = []
        for idx, p in enumerate(lines[1:1 + n]):
            arr, jid, pri, dur, res = int(p[0]), p[1], int(p[2]), int(p[3]), int(p[4])
            if arr < 0 or dur < 1 or res < 1:
                raise ValueError
            jobs.append((arr, idx, jid, pri, dur))
        if len(jobs) != n or not 1 <= w <= 64:
            raise ValueError
    except (IndexError, ValueError):
        print("Input error")
        return

    jobs.sort()                                       # by arrival time, then input order
    sched, pending, i, total_wait = Scheduler(w), [], 0, 0
    while i < n or pending:
        t, wid = sched.acquire_worker()               # take the earliest free worker
        if not pending and jobs[i][0] > t:
            t = jobs[i][0]                            # worker waits for the next job
        while i < n and jobs[i][0] <= t:              # add every job that has arrived
            arr, idx, jid, pri, dur = jobs[i]
            heapq.heappush(pending, (-pri, arr, idx, jid, dur))
            i += 1
        _p, arr, _idx, jid, dur = heapq.heappop(pending)   # highest priority first
        print(jid, f"W{wid}", t, t + dur)
        total_wait += t - arr
        sched.release_worker(t + dur, wid)
    print(f"AVG_WAIT {total_wait / n:.2f}")


if __name__ == "__main__":
    main()