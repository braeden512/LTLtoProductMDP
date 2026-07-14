# import train module
from lcrl.train import train
# either create an environment object or import built-in ones
from lcrl.environments.minecraft import minecraft


if __name__ == "__main__":
    MDP = minecraft
    # this script converts an LTL formula to an LDBA via OWL and then trains on the product MDP
    ltl_formula = 'F (wood & X F tool_shed)'

    print('LTL formula:', ltl_formula)
    task = train(MDP, ltl_formula,
                 algorithm='ql',
                 episode_num=500,
                 iteration_num_max=4000,
                 discount_factor=0.95,
                 learning_rate=0.9
                 )
