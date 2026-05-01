from singleintegrator import SingleIntegrator
from pytorch_mppi import MPPI
import torch
import json

print(MPPI)
print("herro")

class MPPIinputs:
    def __init__(self, dt, goal):
        self.dt = dt
        self.goal = torch.tensor(goal, dtype=torch.float32)

    def dynamics(self, x, u):
        return x + u * self.dt
    
    def rankings(self, planner_output):
        ranking = []
        with open(planner_output, 'r') as file:
            content = json.load(file)
            for evaluation in content["CandidateEvals"]:
                ranking.append(evaluation["rank"])
        return ranking
    
    def cost(self, x, u) -> torch.Tensor:
        goal = self.goal.to(device=x.device, dtype=x.dtype)
        diff = x - goal
        goal_cost = (diff ** 2).sum(dim=1)
        return goal_cost
    
MPPI(
    dynamics= SingleIntegrator,
    running_cost= MPPIinputs.cost(x, u),
    nx = 0,
    noise_sigma= 0,
    num_samples= 500,
    horizon= 30,
    device= "cpu",
    terminal_state_cost= None
    lambda_= 0.06,
    u_min = 

     )