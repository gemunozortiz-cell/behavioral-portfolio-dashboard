"""Políticas: baseline, PFA (bandas), CFA (re-optimización anual) y conductuales."""
import numpy as np
from .portfolio import solve_cvar_milp, cvar_limit

BH = "Comprar y mantener"
PFA = "Rebalanceo por bandas"
CFA = "Re-optimización anual"
PANIC = "Venta por pánico"
CHASE = "Persecución de rendimiento"
CLIENT = "Tú tal como eres"


def _rows(target, S):
    t = np.asarray(target, dtype=float)
    if t.ndim == 1:
        t = np.broadcast_to(t, (S, t.size))
    return np.array(t, dtype=float, copy=True)


class Policy:
    name = "Política"
    klass = ""

    def params(self):
        return {}

    def reset(self, S, N):
        self.S, self.N = S, N

    def decide(self, st):
        raise NotImplementedError

    def target_weights(self):
        raise NotImplementedError


class BuyAndHold(Policy):
    """Baseline: compra el portafolio objetivo en t = 0 y no vuelve a operar."""
    klass = "Baseline"

    def __init__(self, target, name=BH):
        self.target0 = np.asarray(target, dtype=float)
        self.name = name

    def reset(self, S, N):
        super().reset(S, N)
        self.T = _rows(self.target0, S)

    def target_weights(self):
        return self.T

    def decide(self, st):
        return self.T.copy() if st.t == 0 else st.w


class BandRebalancing(Policy):
    """PFA: vuelve a los pesos objetivo cuando algún peso se aleja más de b."""
    klass = "PFA"

    def __init__(self, target, b, name=PFA):
        self.target0 = np.asarray(target, dtype=float)
        self.b = float(b)
        self.name = name

    def params(self):
        return {"b": self.b}

    def reset(self, S, N):
        super().reset(S, N)
        self.T = _rows(self.target0, S)

    def target_weights(self):
        return self.T

    def decide(self, st):
        if st.t == 0:
            return self.T.copy()
        out = st.w.copy()
        hit = np.abs(st.w - self.T).max(axis=1) > self.b
        out[hit] = self.T[hit]
        return out


class AnnualReoptimization(Policy):
    """CFA: cada `every` meses resuelve el MILP con límite c(λ)·θ sobre los últimos `window` meses."""
    klass = "CFA"
    _cache = {}

    def __init__(self, lam, theta, window, cons, A, hist, every=12, name=CFA):
        self.lam, self.theta, self.window = float(lam), float(theta), int(window)
        self.cons, self.A = cons, np.asarray(A, dtype=float)
        self.hist = np.asarray(hist, dtype=float)
        self.every, self.name = int(every), name
        self.limit = cvar_limit(self.lam, self.theta)
        self.n_solves = 0

    def params(self):
        return {"theta": self.theta, "window": self.window}

    def _solve(self, R):
        w, _ = solve_cvar_milp(R, self.A, self.cons, self.limit)
        self.n_solves += 1
        return w

    def reset(self, S, N):
        super().reset(S, N)
        key = (self.lam, self.theta, self.window, self.cons, self.hist.shape, float(self.hist.sum()))
        if key not in AnnualReoptimization._cache:      # en t = 0 todos los escenarios comparten la historia
            AnnualReoptimization._cache[key] = self._solve(self.hist[-self.window:])
        self.T = _rows(AnnualReoptimization._cache[key], S)

    def target_weights(self):
        return self.T

    def decide(self, st):
        if st.t == 0:
            return self.T.copy()
        if st.t % self.every == 0:
            for s in range(self.S):
                R = np.concatenate([self.hist, st.past[s]], axis=0)[-self.window:]
                self.T[s] = self._solve(R)
            return self.T.copy()
        return st.w


class PanicSelling(Policy):
    """Conductual: tras una caída d vende la fracción φ a efectivo; vuelve tras un rebote r desde el mínimo."""
    klass = "Conductual"

    def __init__(self, base, d, r, phi, cash_idx, name=PANIC):
        self.base, self.d, self.r, self.phi = base, float(d), float(r), float(phi)
        self.cash_idx, self.name = int(cash_idx), name

    def params(self):
        return {"d": self.d, "r": self.r, "phi": self.phi}

    def reset(self, S, N):
        super().reset(S, N)
        self.base.reset(S, N)
        self.in_cash = np.zeros(S, dtype=bool)
        self.ref_peak = np.full(S, -np.inf)
        self.trough = np.full(S, np.inf)
        self.e_cash = np.zeros(N)
        self.e_cash[self.cash_idx] = 1.0

    def target_weights(self):
        return self.base.target_weights()

    def decide(self, st):
        W = st.W
        inv = ~self.in_cash
        self.ref_peak[inv] = np.maximum(self.ref_peak[inv], W[inv])
        self.trough[self.in_cash] = np.minimum(self.trough[self.in_cash], W[self.in_cash])
        drawdown = 1.0 - W / self.ref_peak
        trigger = inv & (drawdown >= self.d)
        reenter = self.in_cash & (W >= self.trough * (1.0 + self.r))
        hold = self.in_cash & ~reenter

        out = self.base.decide(st)
        if trigger.any():
            out[trigger] = (1.0 - self.phi) * st.w[trigger] + self.phi * self.e_cash
        out[hold] = st.w[hold]
        if reenter.any():
            out[reenter] = self.base.target_weights()[reenter]

        self.in_cash[trigger] = True
        self.trough[trigger] = W[trigger]
        self.in_cash[reenter] = False
        self.ref_peak[reenter] = W[reenter]
        return out


class PerformanceChasing(Policy):
    """Conductual: cada f meses inclina el objetivo de la PFA hacia los top-k ganadores de 12 meses."""
    klass = "Conductual"

    def __init__(self, base, kappa, f, top_k=3, name=CHASE):
        self.base, self.kappa, self.f, self.top_k = base, float(kappa), int(f), int(top_k)
        self.name = name

    def params(self):
        return {"kappa": self.kappa, "f": self.f, "top_k": self.top_k}

    def reset(self, S, N):
        super().reset(S, N)
        self.base.reset(S, N)
        self.T0 = self.base.target_weights().copy()

    def target_weights(self):
        return self.base.target_weights()

    def decide(self, st):
        if st.t > 0 and st.t % self.f == 0 and self.kappa > 0:
            cum = np.prod(1.0 + st.recent, axis=1) - 1.0                  # (S, N) retorno a 12 meses
            top = np.argsort(-cum, axis=1)[:, :self.top_k]
            winners = np.zeros_like(cum)
            np.put_along_axis(winners, top, 1.0 / self.top_k, axis=1)
            self.base.T = (1.0 - self.kappa) * self.T0 + self.kappa * winners
            return self.base.T.copy()
        return self.base.decide(st)


def standard_policies(profile, w_star, b, cash_idx, cfa=None):
    """El conjunto de políticas que se compara en el notebook y en la app (mismos nombres y reglas)."""
    pols = [BuyAndHold(w_star), BandRebalancing(w_star, b)]
    if cfa is not None:
        pols.append(AnnualReoptimization(profile.lam, cfa["theta"], cfa["window"], cfa["cons"], cfa["A"], cfa["hist"]))
    pols.append(PanicSelling(BandRebalancing(w_star, b), profile.d, profile.r, profile.phi, cash_idx))
    pols.append(PerformanceChasing(BandRebalancing(w_star, b), profile.kappa, profile.f, profile.top_k))
    client = BandRebalancing(w_star, b, name=CLIENT)
    if profile.chase:
        client = PerformanceChasing(client, profile.kappa, profile.f, profile.top_k, name=CLIENT)
    if profile.panic:
        client = PanicSelling(client, profile.d, profile.r, profile.phi, cash_idx, name=CLIENT)
    client.klass = "Conductual (perfil)"
    pols.append(client)
    return pols
