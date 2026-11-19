"""Parte 2: portafolio media-CVaR (MILP, linealización de Rockafellar–Uryasev) con Gurobi."""
from dataclasses import dataclass
import numpy as np
import pandas as pd

C_MAX, C_MIN = 0.10, 0.02
_ENV = None


@dataclass(frozen=True)
class Constraints:
    K: int = 8                 # máximo de activos
    l: float = 0.05            # posición mínima si el activo entra
    u: float = 0.35            # posición máxima
    class_cap: float = 0.50    # tope por clase de activo ("sector")
    beta: float = 0.95         # nivel del CVaR


@dataclass
class Portfolio:
    weights: pd.Series         # pesos por ticker (fracción)
    mean: float                # retorno mensual esperado (histórico)
    cvar: float                # CVaR mensual histórico (pérdida, fracción)
    cvar_limit: float          # límite c(λ)·θ usado
    status: str

    def table(self, wealth=None):
        from .data import UNIVERSE, NAMES
        w = self.weights[self.weights > 0].sort_values(ascending=False)
        out = pd.DataFrame({"Nombre": [NAMES.get(t, t) for t in w.index],
                            "Clase": [UNIVERSE.get(t, "") for t in w.index],
                            "Peso": w.values}, index=w.index)
        if wealth is not None:
            out["Monto a invertir (US$)"] = w.values * wealth
        return out


def cvar_limit(lam, theta=1.0, c_max=C_MAX, c_min=C_MIN):
    """Límite de CVaR mensual: baja en línea recta de c_max (λ = 1) a c_min (λ = 5)."""
    lam = float(np.clip(lam, 1.0, 5.0))
    return float(theta * (c_max - (c_max - c_min) * (lam - 1.0) / 4.0))


def hist_cvar(port_returns, beta=0.95):
    """CVaR histórico de la pérdida (mínimo de la función de Rockafellar–Uryasev)."""
    losses = -np.asarray(port_returns, dtype=float)
    var = np.quantile(losses, beta, method="inverted_cdf")
    return float(var + np.maximum(losses - var, 0.0).sum() / ((1.0 - beta) * losses.size))


def class_matrix(tickers, classes):
    """Matriz A (clases × activos) con A[c, i] = 1 si el activo i pertenece a la clase c."""
    names = list(dict.fromkeys(classes[t] for t in tickers))
    A = np.array([[1.0 if classes[t] == c else 0.0 for t in tickers] for c in names])
    return A, names


def _env():
    global _ENV
    if _ENV is None:
        import gurobipy as gp
        _ENV = gp.Env(empty=True)
        _ENV.setParam("OutputFlag", 0)
        _ENV.start()
    return _ENV


def solve_cvar_milp(R, A, cons, limit, time_limit=10.0):
    """Resuelve el MILP media-CVaR sobre los escenarios R (S × N). Devuelve (pesos, estado)."""
    import gurobipy as gp
    from gurobipy import GRB

    R = np.asarray(R, dtype=float)
    A = np.asarray(A, dtype=float)
    S, N = R.shape
    if cons.K * cons.u < 1.0 - 1e-9:
        raise ValueError("Infactible: K · u < 1 (no se puede invertir el 100%).")
    mu = R.mean(axis=0)
    coef = np.full(S, 1.0 / ((1.0 - cons.beta) * S))

    def run(with_limit):
        m = gp.Model(env=_env())
        m.Params.TimeLimit = time_limit
        m.Params.MIPGap = 1e-6
        w = m.addMVar(N, lb=0.0, ub=1.0, name="w")
        z = m.addMVar(N, vtype=GRB.BINARY, name="z")
        zeta = m.addMVar(1, lb=-GRB.INFINITY, name="zeta")
        exc = m.addMVar(S, lb=0.0, name="u")
        m.addConstr(w.sum() == 1.0)
        m.addConstr(z.sum() <= cons.K)
        m.addConstr(w - cons.l * z >= 0)
        m.addConstr(w - cons.u * z <= 0)
        m.addConstr(A @ w <= cons.class_cap)
        m.addConstr(R @ w + exc + np.ones((S, 1)) @ zeta >= 0)      # u_s ≥ −r_s·w − ζ
        cvar = zeta[0] + coef @ exc
        if with_limit:
            m.addConstr(cvar <= limit)
            m.setObjective(mu @ w, GRB.MAXIMIZE)
        else:
            m.setObjective(cvar, GRB.MINIMIZE)
        m.optimize()
        x = w.X.copy() if m.SolCount > 0 else None
        opt = m.Status == GRB.OPTIMAL
        m.dispose()
        return x, opt

    x, opt = run(True)
    if x is not None:
        status = "óptimo" if opt else "factible (límite de tiempo)"
    else:
        x, _ = run(False)
        if x is None:
            raise RuntimeError("El MILP no encontró solución: revisa K, l, u y el tope por clase.")
        status = "límite de CVaR infactible: se usó el portafolio de mínimo CVaR"
    x = np.where(x < 1e-7, 0.0, x)
    return x / x.sum(), status


def build_portfolio(profile, returns, cons=Constraints(), theta=1.0, classes=None):
    """Perfil (o λ) + retornos históricos (DataFrame) + restricciones → Portfolio."""
    from .data import UNIVERSE
    classes = classes or UNIVERSE
    lam = getattr(profile, "lam", profile)
    tickers = list(returns.columns)
    A, _ = class_matrix(tickers, classes)
    R = returns.to_numpy(dtype=float)
    limit = cvar_limit(lam, theta)
    w, status = solve_cvar_milp(R, A, cons, limit)
    pr = R @ w
    return Portfolio(pd.Series(w, index=tickers), float(pr.mean()), hist_cvar(pr, cons.beta), limit, status)
