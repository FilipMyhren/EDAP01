
import random
import numpy as np

from models import TransitionModel,ObservationModel,StateModel

#
# Add your Robot Simulator here
#
class RobotSim:
    def __init__(self, current_state, tm):
        self.current_state = current_state
        self.tm = tm
        
    def move(self, new_state):
        temp = self.tm.get_T()[new_state]
        current_state = np.random.choice(range(len(temp)), p=temp)
        return current_state
        
        
#
# Add your Filtering approach here (or within the Localiser, that is your choice!)
#
class HMMFilter:
    def __init__(self, sm, tm, probs):
        self.sm = sm
        self.tm = tm
        self.probs = probs
        
    def forward(self, state):
        alpha = 1/sum(self.probs)
        self.probs = alpha*self.sm.get_o_reading(state) @ self.tm.get_T_transp() @ self.probs
        return self.probs

