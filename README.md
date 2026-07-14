# LTLtoProductMDP

## Quick example of how LCRL and OWL might combine to create a working flow

Product MDP not explicitly shown, LCRL makes something called on-the-fly product mdp, aka it only constructs the product states that the agent actually visits.

To run you must:

make a virtal environment,

install owl and ensure it works with `owl --help`

run an LTL formula on an environment mdp (all are listed in the environments folder) with a command like this:

`MPLBACKEND=Agg PYTHONPATH=src python - <<'PY'
from lcrl.train import train
from lcrl.environments.gridworld_1 import gridworld_1
train(
    gridworld_1,
    'F (goal1 & X F goal2)',
    algorithm='ql',
    episode_num=300,
    iteration_num_max=4000,
    discount_factor=0.95,
    learning_rate=0.9,
    epsilon=0.0,
    test=True
)
PY`

In this example the LTL formla is F(goal1 & X F goal2) and the environment is gridworld_1

Check success rate in testing to evaluate whether the learned policy satisfies the specification.
