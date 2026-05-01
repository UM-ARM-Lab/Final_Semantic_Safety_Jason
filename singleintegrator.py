import torch


class SingleIntegrator:
    """
    Batched single integrator dynamics

        x_{t+1} = x_t + dt * u_t

    State:
        x ∈ R^d

    Action:
        u ∈ R^d
    """

    def __init__(self, state_dim: int, dt: float):
        self.state_dim = state_dim
        self.action_dim = state_dim
        self.dt = dt

    def step(self, x: torch.Tensor, u: torch.Tensor) -> torch.Tensor:
        """
        Propagate one step.

        Parameters
        ----------
        x : (B, d)
            Current states
        u : (B, d)
            Control inputs

        Returns
        -------
        x_next : (B, d)
        """
        assert x.shape == u.shape
        return x + self.dt * u

    def rollout(self, x0: torch.Tensor, U: torch.Tensor) -> torch.Tensor:
        """
        Batched rollout.

        Parameters
        ----------
        x0 : (B, d)
            Initial states
        U : (B, T, d)
            Control sequence

        Returns
        -------
        X : (B, T+1, d)
        """
        B, T, d = U.shape
        X = torch.zeros(B, T + 1, d, device=x0.device)

        X[:, 0] = x0
        x = x0

        for t in range(T):
            x = self.step(x, U[:, t])
            X[:, t + 1] = x

        return X