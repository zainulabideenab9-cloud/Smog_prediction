"""Small DSA components used by LahoreSmog.

These are intentionally simple and explainable for a semester viva.
"""

from __future__ import annotations

import heapq
from collections import deque


class SlidingWindowMean:
    """Maintain a rolling mean in O(1) amortised time per update.

    A deque stores the current window and a running sum avoids recomputing the
    whole window for every new hourly reading.
    """

    def __init__(self, window_size: int) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        self.window_size = window_size
        self.values: deque[float] = deque()
        self.total = 0.0

    def add(self, value: float) -> float:
        self.values.append(value)
        self.total += value
        if len(self.values) > self.window_size:
            self.total -= self.values.popleft()
        return self.total / len(self.values)


class AlertPriorityQueue:
    """Priority queue for alerts, highest AQI first.

    Python heapq is a min-heap, so negative AQI is stored to pop the most
    severe alert first. Push and pop are O(log n).
    """

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, dict]] = []
        self._counter = 0

    def push(self, alert: dict) -> None:
        heapq.heappush(self._heap, (-int(alert["aqi"]), self._counter, alert))
        self._counter += 1

    def pop(self) -> dict:
        if not self._heap:
            raise IndexError("pop from empty alert queue")
        return heapq.heappop(self._heap)[2]

    def __len__(self) -> int:
        return len(self._heap)


def bfs_zone_order(graph: dict[str, list[str]], start: str) -> list[str]:
    """Breadth-first traversal of neighbouring Lahore zones in O(V + E)."""
    visited = {start}
    queue: deque[str] = deque([start])
    order: list[str] = []

    while queue:
        zone = queue.popleft()
        order.append(zone)
        for neighbour in graph.get(zone, []):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)
    return order
