# LTLtoProductMDP

Braeden Treutel **(@braeden512)**

This repository is a practical extension of **LCRL (Logically-Constrained Reinforcement Learning)** workflows for training policies under LTL specifications.  
It keeps the original LCRL core idea: an **on-the-fly product MDP** is explored during learning rather than precomputing the full product.

## What this project currently includes

- LCRL training pipeline under `src/lcrl`
- Custom deterministic `OrderedGoalGrid` environment in `src/lcrl/environments/ordered_goal_grid.py`
- Example training entrypoint in `training_script.py`
- LTL-to-automaton flow through OWL when formulas are passed as strings

## Current training example

`training_script.py` trains Q-learning on `OrderedGoalGrid` with the ordered-goal task:

`G(!obstacle) & F(goal1 & F(goal2 & F(end)))`

This means: always avoid obstacle labels, then eventually reach `goal1`, then `goal2`, then `end`.

## Setup

1. Create and activate a virtual environment.
2. Install this project:

```bash
pip install -e .
```

3. Install OWL and verify it is available:

```bash
owl --help
```

If OWL is not on `PATH`, pass `owl_binary=...` to `train(...)`.

## Run

```bash
python training_script.py
```

You should see training logs and a testing success rate. Result artifacts are saved under `./results/<timestamp>/`.

## Minimal direct invocation example

```bash
MPLBACKEND=Agg PYTHONPATH=src python - <<'PY'
from lcrl.train import train
from lcrl.environments.ordered_goal_grid import OrderedGoalGrid
train(
    OrderedGoalGrid(),
    'G(!obstacle) & F(goal1 & F(goal2 & F(end)))',
    algorithm='ql',
    episode_num=20000,
    iteration_num_max=4000,
    discount_factor=0.95,
    learning_rate=0.9,
    epsilon=0.0,
    test=True,
)
PY
```

![Example run of training_script.py](results/03.08.2026_11.50.51/animation/executed_policy.gif)
