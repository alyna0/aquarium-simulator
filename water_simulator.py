"""Simple 2D water surface simulator.

This script uses a discrete wave equation to simulate ripples on a water surface.
Run directly to see a small ASCII animation in the terminal.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field


@dataclass
class WaterSimulator:
    width: int = 40
    height: int = 20
    damping: float = 0.99
    current: list[list[float]] = field(init=False)
    previous: list[list[float]] = field(init=False)

    def __post_init__(self) -> None:
        self.current = [[0.0 for _ in range(self.width)] for _ in range(self.height)]
        self.previous = [[0.0 for _ in range(self.width)] for _ in range(self.height)]

    def add_drop(self, x: int, y: int, strength: float = 8.0) -> None:
        """Add energy at a point to create a ripple."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.current[y][x] += strength

    def step(self) -> None:
        """Advance one simulation step using a simple wave update."""
        next_grid = [[0.0 for _ in range(self.width)] for _ in range(self.height)]

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                neighbor_avg = (
                    self.current[y - 1][x]
                    + self.current[y + 1][x]
                    + self.current[y][x - 1]
                    + self.current[y][x + 1]
                ) / 2.0
                next_grid[y][x] = (neighbor_avg - self.previous[y][x]) * self.damping

        self.previous, self.current = self.current, next_grid

    def render_ascii(self) -> str:
        """Render the water height map as ASCII characters."""
        chars = " .:-=+*#%@"
        lines = []
        for row in self.current:
            line = ""
            for value in row:
                normalized = min(max((value + 10.0) / 20.0, 0.0), 1.0)
                index = int(normalized * (len(chars) - 1))
                line += chars[index]
            lines.append(line)
        return "\n".join(lines)


def run_demo(frames: int = 120, delay: float = 0.05) -> None:
    simulator = WaterSimulator()

    for frame in range(frames):
        if frame % 15 == 0:
            simulator.add_drop(
                random.randint(5, simulator.width - 6),
                random.randint(5, simulator.height - 6),
                strength=random.uniform(6.0, 12.0),
            )

        simulator.step()

        print("\x1b[2J\x1b[H", end="")
        print("Simple Water Simulator (ASCII)")
        print(simulator.render_ascii())
        time.sleep(delay)


if __name__ == "__main__":
    run_demo()
