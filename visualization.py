import matplotlib.pyplot as plt
import numpy as np

# Environment dimensions
ROWS = 20
COLS = 30

# Create empty grid
grid = np.zeros((ROWS, COLS))

# Coordinates
start = (19, 0)
goal1 = (16, 12)
goal2 = (6, 14)
end = (1, 17)

obstacles = [
    (3, 2),
    (3, 9),
    (8, 12),
    (7, 20),
    (12, 2),
    (14, 9),
]

# Color codes
# 0 = empty
# 1 = obstacle
# 2 = start
# 3 = goal1
# 4 = goal2
# 5 = end

for r, c in obstacles:
    grid[r, c] = 1

grid[start] = 2
grid[goal1] = 3
grid[goal2] = 4
grid[end] = 5

colors = [
    "#FFFFFF",   # empty
    "#333333",   # obstacle
    "#2ECC71",   # start
    "#3498DB",   # goal1
    "#F39C12",   # goal2
    "#E74C3C",   # end
]

from matplotlib.colors import ListedColormap
cmap = ListedColormap(colors)

plt.figure(figsize=(12,8))
plt.imshow(grid, cmap=cmap, origin="upper")

# Draw grid lines
plt.xticks(np.arange(-0.5, COLS, 1), minor=True)
plt.yticks(np.arange(-0.5, ROWS, 1), minor=True)
plt.grid(which="minor", color="gray", linewidth=0.5)

# Remove major ticks
plt.xticks(range(COLS))
plt.yticks(range(ROWS))

# Labels
plt.text(start[1], start[0], "S", ha="center", va="center", color="white", fontsize=12, weight="bold")
plt.text(goal1[1], goal1[0], "1", ha="center", va="center", color="white", fontsize=12, weight="bold")
plt.text(goal2[1], goal2[0], "2", ha="center", va="center", color="white", fontsize=12, weight="bold")
plt.text(end[1], end[0], "E", ha="center", va="center", color="white", fontsize=12, weight="bold")

plt.title("OrderedGoalGrid Environment (30 × 20)")
plt.xlabel("Column")
plt.ylabel("Row")

plt.tight_layout()
plt.show()