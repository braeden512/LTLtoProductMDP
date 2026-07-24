import numpy as np

from lcrl.environments.SlipperyGrid import SlipperyGrid


class OrderedGoalGrid(SlipperyGrid):
    """Deterministic 30x20 grid with ordered goals and terminal obstacles."""

    def __init__(self):
        self.shape = [20, 30]  # 20 rows x 30 columns
        self.start_state = [19, 0]  # bottom-left corner
        self.goal_1_state = [16, 12]
        self.goal_2_state = [6, 14]
        self.end_state = [1, 17]
        self.obstacle_states = [
            [3, 2],
            [3, 9],
            [8, 12],
            [7, 20],
            [12, 2],
            [14, 9],
        ]

        super().__init__(
            shape=self.shape,
            initial_state=self.start_state,
            slip_probability=0.0,
            sink_states=self.obstacle_states,
        )

        # Cardinal moves only.
        self.action_space = ["right", "up", "left", "down"]

        self.reached_goal_1 = False
        self.reached_goal_2 = False
        self.done = False
        self.termination_reason = None

        self.labels = np.empty([self.shape[0], self.shape[1]], dtype=object)
        self.reset()

    def _build_labels(self):
        self.labels[:, :] = "safe"
        for row, col in self.obstacle_states:
            self.labels[row, col] = "obstacle"

        self.labels[self.goal_1_state[0], self.goal_1_state[1]] = "goal1"
        self.labels[self.goal_2_state[0], self.goal_2_state[1]] = "goal2"
        self.labels[self.end_state[0], self.end_state[1]] = "end"

    def reset(self):
        self.current_state = self.start_state.copy()
        self.reached_goal_1 = False
        self.reached_goal_2 = False
        self.done = False
        self.termination_reason = None
        self._build_labels()

    def step(self, action):
        if action not in self.action_space:
            raise ValueError(f"Invalid action '{action}'. Allowed actions: {self.action_space}")

        if self.done:
            return self.current_state

        row, col = self.current_state
        if action == "right":
            col = min(col + 1, self.shape[1] - 1)
        elif action == "up":
            row = max(row - 1, 0)
        elif action == "left":
            col = max(col - 1, 0)
        elif action == "down":
            row = min(row + 1, self.shape[0] - 1)

        next_state = [row, col]
        self.current_state = next_state

        if next_state in self.obstacle_states:
            self.done = True
            self.termination_reason = "obstacle"
        elif next_state == self.goal_1_state:
            self.reached_goal_1 = True
        elif next_state == self.goal_2_state and self.reached_goal_1:
            self.reached_goal_2 = True
        elif next_state == self.end_state and self.reached_goal_1 and self.reached_goal_2:
            self.done = True
            self.termination_reason = "success"

        return next_state
