"""Escenarios: bootstrap circular por bloques de 3 a 6 meses (filas históricas completas)."""
from dataclasses import dataclass
import numpy as np

TUNE_SEED = 2026
EVAL_SEED = 7777
HORIZON = 120


@dataclass
class Scenarios:
    returns: np.ndarray        # (S, H, N) retornos mensuales simulados
    index: np.ndarray          # (S, H) fila histórica usada en cada mes
    block_lengths: list        # por escenario: longitudes de bloque (la última puede venir truncada)
    seed: int

    @property
    def n(self):
        return self.returns.shape[0]

    def subset(self, n):
        return Scenarios(self.returns[:n], self.index[:n], self.block_lengths[:n], self.seed)


def block_bootstrap(hist, n_scen, horizon=HORIZON, seed=0, min_block=3, max_block=6):
    hist = np.asarray(hist, dtype=float)
    T = hist.shape[0]
    rng = np.random.default_rng(seed)
    idx = np.empty((n_scen, horizon), dtype=np.int64)
    lengths = []
    for s in range(n_scen):
        t, ls = 0, []
        while t < horizon:
            L = int(rng.integers(min_block, max_block + 1))
            start = int(rng.integers(0, T))
            take = min(L, horizon - t)
            idx[s, t:t + take] = (start + np.arange(take)) % T
            ls.append(take)
            t += take
        lengths.append(np.array(ls))
    return Scenarios(hist[idx], idx, lengths, seed)
