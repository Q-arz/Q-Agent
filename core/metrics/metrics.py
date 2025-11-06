import time
from collections import defaultdict


class Metrics:
    def __init__(self):
        self.counters = defaultdict(int)
        self.timings = defaultdict(list)

    def inc(self, key: str, value: int = 1):
        self.counters[key] += value

    def time_block(self, key: str):
        start = time.time()
        def end():
            self.timings[key].append(time.time() - start)
        return end

metrics = Metrics()


