from lcrl.train import train
from lcrl.environments.ordered_goal_grid import OrderedGoalGrid

train( 
  # 30x20 new environment
  OrderedGoalGrid(),
  # LTL formula: Always avoid obstacles, and eventually reach goal1, then goal2, then the end
  'G(!obstacle) & F(goal1 & F(goal2 & F(end)))',
  # eventually replace with MAPPO
  algorithm='ql', 
  episode_num=10000, 
  iteration_num_max=4000, 
  discount_factor=0.95, 
  learning_rate=0.9, 
  epsilon=0.0, 
  test=True,
)