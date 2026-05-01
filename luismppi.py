"""Model Predictive Path Integral Planner Implementation."""

import logging
import time
from collections.abc import Callable

import torch
from torch.distributions import MultivariateNormal

from luis_utils.geometry import Gaussian

logger = logging.getLogger(__name__)



class MPPI:
    """Model Predictive Path Integral Planner."""

    def __init__(
        self,
        optimization_problem,
        dynamics_model: Callable,
        ego_idx: int,
        ctrl_args: dict,
        post_rollout_fn: Callable | None = None,
    ):
        self.EGO_IDX: int = ego_idx

        self.optimization_problem = optimization_problem

        self.subgoal_index: int = 0
        self.optimization_problem.bind_get_subgoal(lambda: self.optimization_problem.subgoals[self.subgoal_index].flatten())
        self.H: int = optimization_problem.H
        bounds = self.optimization_problem.constraint_fns["ControlBoxConstraint"].get_bounds()
        self.A_DIM: int = bounds.shape[-1]
        logger.info("Horizon: %d", self.H)

        self.N: int = ctrl_args["num_samples"]  # Number of trajectories to sample
        self.lambda_: float = ctrl_args["lambda_"]

        self.dynamics: Callable = dynamics_model

        self.all_costs = torch.full(
            (self.N,),
            float("nan"),
        )  # (N)

        noise_mu = ctrl_args.get("noise_mu")
        noise_sigma = torch.tensor(ctrl_args["noise_sigma"])
        u_min = bounds[0]
        u_max = bounds[1]
        u_per_command = ctrl_args.get("u_per_command", 1)
        U_init = ctrl_args.get("U_init")

        # Noise
        if noise_mu is None:
            noise_mu = torch.zeros(self.A_DIM)  # (A_DIM,)
        assert noise_sigma.shape == (self.A_DIM, self.A_DIM)
        assert noise_mu.shape == (self.A_DIM,) == u_max.shape == u_min.shape

        self.noise_sigma_inv = torch.inverse(noise_sigma)
        # Mean (A_DIM,), Cov (A_DIM, A_DIM)
        self.noise_dist = MultivariateNormal(noise_mu, covariance_matrix=noise_sigma)  # type: ignore[no-untyped-call]
        self.u_min: torch.Tensor = u_min
        self.u_max: torch.Tensor = u_max
        self.u_per_command = u_per_command
        self.executed_trajectory: dict[str, torch.Tensor] = {}
        self.approximate_starting_covariance = ctrl_args["approximate_starting_covariance"]  # State covariance for first step of planning trajectory

        if U_init is None:
            self.U: torch.Tensor = self.noise_dist.sample(torch.Size([self.H]))  # (H, A_DIM) - Initial control sequence
        else:
            self.U = U_init

        self.sample_null_action: bool = ctrl_args["sample_null_action"]
        self.post_rollout_fn: Callable | None = post_rollout_fn

        self.online_iterations: int = ctrl_args["online_iterations"]
        self.warmup_iterations: int = ctrl_args["warmup_iterations"]
        self.warmed_up: bool = False
        self.individual_costs: dict[str, torch.Tensor] = {}
        self.iteration_traces: list[dict[str, object]] = []

    def _rollout_dynamics(self, dyn_func, s0: Gaussian, U, replicate_s0: bool):
        """
        Rollout dynamics for planning horizon.

        Args:
            dyn_func: Dynamics function (approximate_step)
            s0: Initial state (STATE_DIM, 1) or (N, STATE_DIM)
            U: Control sequence (N, H, A_DIM)
            replicate_s0: Whether to replicate s0 for all samples

        """
        states = []
        assert isinstance(s0, Gaussian), f"Expected state to be a Gaussian, got {type(s0)}."

        if replicate_s0:  # TODO this if-else is unclear
            s = s0.mean.reshape(1, -1).repeat(U.shape[0], 1)  # (N, STATE_DIM)
            cov = s0.covariance_matrix.repeat(U.shape[0], 1, 1)  # (N, STATE_DIM, STATE_DIM)
        else:
            # When replicate_s0=False, s0 is already batched correctly
            s = s0.mean  # Already (1, STATE_DIM) - no transpose needed!
            cov = s0.covariance_matrix  # Already (1, STATE_DIM, STATE_DIM)

        # Wrap initial state in Gaussian for first step
        s = Gaussian(mean=s, covariance=cov)

        for t in range(self.H):
            s = dyn_func(s, U[:, t], t=t)
            states.append(s)

        return states

    def command(self, state, _belief_map) -> torch.Tensor:
        """
        :param state: (nx) or (K x nx) current state, or samples of states (for propagating a distribution of states)
        :param shift_nominal_trajectory: Whether to roll the nominal trajectory forward one step. This should be True
        if the command is to be executed. If the nominal trajectory is to be refined then it should be False.
        :returns action: (nu) best action



        1st: (4, 1)
        2nd: (N, 4)
        """
        if not isinstance(state, Gaussian):  # TODO: fine to not clone anymore?
            raise TypeError(f"MPPI.command expects a Gaussian state, got {type(state)}.")

        phase_label = "warmup" if not self.warmed_up else "online"
        iterations = self.warmup_iterations if not self.warmed_up else self.online_iterations
        self.iteration_traces = []
        timing_enabled = logger.isEnabledFor(logging.DEBUG)
        timing = {"noise": 0.0, "rollout": 0.0, "cost": 0.0, "update": 0.0, "best": 0.0, "iter_total": 0.0} if timing_enabled else None

        for iter_idx in range(iterations):
            if timing_enabled:
                t_iter = time.perf_counter()
            perturbed_actions = self.U + self.noise_dist.rsample((self.N, self.H))  # (N, H, A_DIM)

            if self.sample_null_action:
                perturbed_actions[self.N - 1] = 0
            perturbed_actions = torch.max(torch.min(perturbed_actions, self.u_max), self.u_min)

            # bounded noise after bounding (some got cut off, so we don't penalize that in action cost)
            noise = perturbed_actions - self.U
            action_cost = torch.sum(self.U * self.lambda_ * noise @ self.noise_sigma_inv, dim=(1, 2))
            if timing_enabled:
                timing["noise"] += time.perf_counter() - t_iter

            total_cost = torch.zeros(self.N)

            if timing_enabled:
                t0 = time.perf_counter()
            rollout_states = self._rollout_dynamics(
                self.dynamics,
                state,
                perturbed_actions,
                replicate_s0=True,
            )
            # Apply per-horizon scaling if configured (e.g., for ACP)
            if self.post_rollout_fn is not None:
                rollout_states = self.post_rollout_fn(rollout_states)
            if timing_enabled:
                timing["rollout"] += time.perf_counter() - t0

            total_cost += action_cost
            if timing_enabled:
                t0 = time.perf_counter()
            planning_cost, debug_costs = self.optimization_problem.cost_fn(rollout_states, perturbed_actions, o=None)
            if timing_enabled:
                timing["cost"] += time.perf_counter() - t0
            self.individual_costs = debug_costs

            total_cost += planning_cost
            if timing_enabled:
                t0 = time.perf_counter()
            total_cost -= torch.min(total_cost)
            omega = torch.softmax(-total_cost / self.lambda_, dim=0)
            self.U = torch.sum((omega.reshape(-1, 1, 1) * perturbed_actions), dim=0)
            if timing_enabled:
                timing["update"] += time.perf_counter() - t0

            self.iteration_traces.append(
                {
                    "phase": phase_label,
                    "iteration": iter_idx,
                    "actions": perturbed_actions.clone(),
                    "costs": total_cost.clone(),
                    "states": rollout_states,
                }
            )
            if timing_enabled:
                timing["iter_total"] += time.perf_counter() - t_iter

        self.all_costs = total_cost
        self.all_states = rollout_states

        best_U = self.U.clone()  # (H, A_DIM)
        if timing_enabled:
            t0 = time.perf_counter()
        best_S = self._rollout_dynamics(self.dynamics, state, best_U.reshape(1, self.H, self.A_DIM), replicate_s0=False)  # (H, STATE_DIM)
        if timing_enabled:
            timing["best"] += time.perf_counter() - t0

        self.executed_trajectory = {"best_S": best_S, "best_U": best_U}  # (H, PLANNING_STATE_DIM + U_DIM)

        action = best_U[: self.u_per_command]  # (u_per_command, A_DIM)

        # reduce dimensionality if we only need the first command
        if self.u_per_command == 1:
            action = action[0]

        self.warmed_up = True
        self.shift()
        if timing_enabled and timing is not None:
            iters = max(iterations, 1)
            logger.debug(
                "MPPI timings (iters=%d, N=%d, H=%d): noise=%.3fs rollout=%.3fs cost=%.3fs update=%.3fs best=%.3fs total=%.3fs",
                iterations,
                self.N,
                self.H,
                timing["noise"],
                timing["rollout"],
                timing["cost"],
                timing["update"],
                timing["best"],
                timing["iter_total"],
            )
        return action

    def shift(self) -> None:
        """Shift the control sequence forward one step."""
        self.U = torch.roll(self.U, shifts=-1, dims=0)
        # self.U[-1] = self.noise_dist.sample()  # TODO: this could be noise or zero, to be changed as hyperameter passed in class instantiation
        self.U[-1] = 0

    def reset(self, *, reset_subgoal_index: bool, reset_controls: bool) -> None:
        """Reset the MPPI planner (to be called between episodes)."""
        logger.info("Resetting MPPI")
        self.warmed_up = False
        self.individual_costs = {}
        if reset_controls:
            self.U = self.noise_dist.sample(torch.Size([self.H]))
        if reset_subgoal_index:
            self.subgoal_index = 0  
