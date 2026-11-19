"""Simulador vectorizado: aplica la función de transición del modelo de Powell mes a mes."""
from dataclasses import dataclass
import numpy as np


@dataclass
class State:
    t: int
    W: np.ndarray          # (S,) riqueza antes de operar, USD
    w: np.ndarray          # (S, N) pesos antes de operar (después de la deriva)
    peak: np.ndarray       # (S,) máximo de riqueza hasta la fecha, USD
    recent: np.ndarray     # (S, 12, N) retornos de los últimos 12 meses
    past: np.ndarray       # (S, t, N) retornos simulados hasta el mes t−1


@dataclass
class SimResult:
    name: str
    klass: str
    wealth: np.ndarray     # (S, H+1) riqueza, USD
    traded: np.ndarray     # (S,) valor total operado, USD
    costs: np.ndarray      # (S,) costos de transacción pagados, USD

    @property
    def terminal(self):
        return self.wealth[:, -1]

    @property
    def max_drawdown(self):
        peak = np.maximum.accumulate(self.wealth, axis=1)
        return (1.0 - self.wealth / peak).max(axis=1)


def simulate(policy, scenarios, hist, W0=100_000.0, cost=0.001):
    scen = getattr(scenarios, "returns", scenarios)
    S, H, N = scen.shape
    hist = np.asarray(hist, dtype=float)
    policy.reset(S, N)
    W = np.full(S, float(W0))
    w = np.zeros((S, N))                          # t = 0: todo el dinero sin invertir
    peak = W.copy()
    recent = np.broadcast_to(hist[-12:], (S, 12, N)).copy()
    path = np.empty((S, H + 1))
    path[:, 0] = W
    traded = np.zeros(S)
    costs = np.zeros(S)
    for t in range(H):
        st = State(t, W.copy(), w.copy(), peak.copy(), recent, scen[:, :t, :])
        x = np.asarray(policy.decide(st), dtype=float)
        if x.shape != (S, N) or (x < -1e-9).any() or not np.allclose(x.sum(axis=1), 1.0, atol=1e-6):
            raise ValueError(f"{policy.name}: pesos inválidos en t = {t}")
        tv = W * np.abs(x - w).sum(axis=1)       # valor operado
        c = cost * tv
        W = W - c
        R = scen[:, t, :]
        gross = 1.0 + (x * R).sum(axis=1)
        W = W * gross
        w = x * (1.0 + R) / gross[:, None]
        peak = np.maximum(peak, W)
        recent = np.concatenate([recent[:, 1:], R[:, None, :]], axis=1)
        traded += tv
        costs += c
        path[:, t + 1] = W
    return SimResult(policy.name, policy.klass, path, traded, costs)
