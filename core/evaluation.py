"""Evaluación: valor PT, intervalos de confianza, comparaciones pareadas, ajuste y recomendación."""
from statistics import NormalDist
import numpy as np
import pandas as pd
from .profile import pt_value
from .simulator import simulate
from .policies import BH, PFA, CFA, PANIC, CHASE, CLIENT
from .i18n import policy_name


def usd(x, lang="es"):
    x = 0.0 if abs(x) < 0.5 else x          # evita "US$ -0"
    s = f"{x:,.0f}"
    return "US$ " + (s if lang == "en" else s.replace(",", "."))


def pt_scores(W_T, W0, W_ref, profile):
    x = (np.asarray(W_T, dtype=float) - W_ref) / W0
    return pt_value(x, profile.alpha, profile.beta, profile.lam)


def certainty_equivalent(mean_pt, profile, W0, W_ref=None):
    """Riqueza segura (US$) cuyo valor PT es igual a `mean_pt`: invierte v y devuelve W_ref + W0·x."""
    W_ref = W0 if W_ref is None else W_ref
    m = float(mean_pt)
    x = m ** (1 / profile.alpha) if m >= 0 else -((-m / profile.lam) ** (1 / profile.beta))
    return W_ref + W0 * x


def summarize(v, level=0.95, n_boot=2000, seed=0):
    """Media, desviación, percentiles e IC (normal y bootstrap percentil) de la media."""
    v = np.asarray(v, dtype=float)
    n = v.size
    m = float(v.mean())
    sd = float(v.std(ddof=1)) if n > 1 else 0.0
    z = NormalDist().inv_cdf(0.5 + level / 2)
    se = sd / np.sqrt(n)
    rng = np.random.default_rng(seed)
    boot = v[rng.integers(0, n, size=(n_boot, n))].mean(axis=1)
    lo, hi = np.quantile(boot, [(1 - level) / 2, (1 + level) / 2])
    p5, p50, p95 = np.percentile(v, [5, 50, 95])
    return {"mean": m, "std": sd, "p5": p5, "p50": p50, "p95": p95,
            "ci_low": m - z * se, "ci_high": m + z * se, "boot_low": lo, "boot_high": hi, "n": n}


def evaluate(policies, scenarios, hist, W0=100_000.0, cost=0.001):
    """Simula todas las políticas sobre el MISMO tensor de escenarios (números aleatorios comunes)."""
    names = [p.name for p in policies]
    assert len(set(names)) == len(names), "los nombres de las políticas deben ser únicos"
    return {p.name: simulate(p, scenarios, hist, W0=W0, cost=cost) for p in policies}


def results_table(results, profile, W0, W_ref=None):
    W_ref = W0 if W_ref is None else W_ref
    rows = []
    for name, res in results.items():
        pt = summarize(pt_scores(res.terminal, W0, W_ref, profile))
        wt = summarize(res.terminal)
        years = (res.wealth.shape[1] - 1) / 12
        rows.append({
            "Política": name, "Clase": res.klass,
            "Valor PT medio": pt["mean"], "Valor PT desv.": pt["std"],
            "Valor PT P5": pt["p5"], "Valor PT P95": pt["p95"],
            "IC95% PT (normal)": f"[{pt['ci_low']:.4f}, {pt['ci_high']:.4f}]",
            "IC95% PT (bootstrap)": f"[{pt['boot_low']:.4f}, {pt['boot_high']:.4f}]",
            "Equivalente cierto (US$)": certainty_equivalent(pt["mean"], profile, W0, W_ref),
            "Riqueza final media": wt["mean"], "Riqueza desv.": wt["std"],
            "Riqueza P5": wt["p5"], "Riqueza P50": wt["p50"], "Riqueza P95": wt["p95"],
            "IC95% riqueza media": f"[{wt['ci_low']:,.0f}, {wt['ci_high']:,.0f}]",
            "Caída máx. mediana": float(np.median(res.max_drawdown)),
            "Costos medios": float(res.costs.mean()),
            "Rotación anual media": float((res.traded / res.wealth.mean(axis=1)).mean() / years),
        })
    return pd.DataFrame(rows).set_index("Política")


def paired_comparison(results, profile, W0, W_ref=None, reference=PFA):
    """Diferencias escenario a escenario frente a la política de referencia."""
    W_ref = W0 if W_ref is None else W_ref
    ref_wt = results[reference].terminal
    ref_pt = pt_scores(ref_wt, W0, W_ref, profile)
    rows = []
    for name, res in results.items():
        if name == reference:
            continue
        dpt = summarize(pt_scores(res.terminal, W0, W_ref, profile) - ref_pt)
        dwt = summarize(res.terminal - ref_wt)
        rows.append({
            "Política": name,
            "Δ valor PT medio": dpt["mean"],
            "IC95% Δ PT": f"[{dpt['ci_low']:.4f}, {dpt['ci_high']:.4f}]",
            "¿Diferencia significativa?": "sí" if (dpt["ci_low"] > 0 or dpt["ci_high"] < 0) else "no",
            "Δ riqueza media (US$)": dwt["mean"],
            "IC95% Δ riqueza": f"[{dwt['ci_low']:,.0f}, {dwt['ci_high']:,.0f}]",
            "Δ riqueza mediana (US$)": float(np.median(res.terminal) - np.median(ref_wt)),
            f"Prob. de superar a «{reference}»": float((res.terminal > ref_wt + 1e-6).mean()),
        })
    return pd.DataFrame(rows).set_index("Política")


def behavior_costs(results, reference=PFA, names=(PANIC, CHASE, CLIENT)):
    """Costo de cada conducta frente a la disciplina (mismos escenarios)."""
    ref = results[reference].terminal
    rows = []
    for name in names:
        if name not in results:
            continue
        wt = results[name].terminal
        d = summarize(ref - wt)
        rows.append({
            "Conducta": name,
            "Costo en la mediana (US$)": float(np.median(ref) - np.median(wt)),
            "Costo medio (US$)": d["mean"],
            "IC95% costo medio": f"[{d['ci_low']:,.0f}, {d['ci_high']:,.0f}]",
            "Escenarios peores que la disciplina": float((wt < ref - 1e-6).mean()),
        })
    return pd.DataFrame(rows).set_index("Conducta")


def fan_quantiles(res, qs=(5, 25, 50, 75, 95)):
    q = np.percentile(res.wealth, qs, axis=0)
    return pd.DataFrame(q.T, columns=list(qs))


def tune(factory, grid, scenarios, hist, profile, W0=100_000.0, W_ref=None, cost=0.001):
    """Búsqueda en cuadrícula: valor PT medio (y su error estándar) para cada combinación de parámetros."""
    W_ref = W0 if W_ref is None else W_ref
    rows = []
    for params in grid:
        res = simulate(factory(**params), scenarios, hist, W0=W0, cost=cost)
        v = pt_scores(res.terminal, W0, W_ref, profile)
        rows.append({**params, "pt_mean": float(v.mean()), "pt_se": float(v.std(ddof=1) / np.sqrt(v.size)),
                     "median_WT": float(np.median(res.terminal)), "mean_costs": float(res.costs.mean())})
    return pd.DataFrame(rows).sort_values("pt_mean", ascending=False).reset_index(drop=True)


def recommend(results, profile, W0, W_ref=None, candidates=(BH, PFA, CFA), level=0.95, lang="es"):
    """Mayor valor PT medio; si una política más simple no es significativamente peor, se elige la simple.
    `candidates` va ordenado de la más simple a la más compleja."""
    W_ref = W0 if W_ref is None else W_ref
    scores = {n: pt_scores(results[n].terminal, W0, W_ref, profile) for n in candidates if n in results}
    best = max(scores, key=lambda n: scores[n].mean())
    chosen = best
    reason = (f"it has the highest expected prospect-theory value ({scores[best].mean():.4f})" if lang == "en" else
              f"tiene el mayor valor esperado de prospect theory ({scores[best].mean():.4f})")
    for n in candidates:
        if n == best:
            break
        if n not in scores:
            continue
        d = summarize(scores[n] - scores[best], level)
        if d["ci_low"] <= 0 <= d["ci_high"]:
            chosen = n
            ci = f"[{d['ci_low']:.4f}, {d['ci_high']:.4f}]"
            if lang == "en":
                reason = (f"it is not significantly worse than «{policy_name(best, lang)}» (the 95% CI of the "
                          f"PT-value difference, {ci}, includes 0) and it is simpler to follow")
            else:
                reason = (f"no es significativamente peor que «{best}» (el IC95% de la diferencia de valor PT, "
                          f"{ci}, incluye 0) y es más simple de seguir")
            break
    return {"chosen": chosen, "best": best, "reason": reason,
            "means": {n: float(v.mean()) for n, v in scores.items()}}


def plain_language(results, W0, W_ref=None, reference=PFA, lang="es"):
    """Una frase por política, sin jerga estadística."""
    W_ref = W0 if W_ref is None else W_ref
    ref = results[reference].terminal
    rname = policy_name(reference, lang)
    out = {}
    for name, res in results.items():
        wt = res.terminal
        p5, p50 = np.percentile(wt, [5, 50])
        below = (wt < W_ref).mean()
        if lang == "en":
            s = (f"Half of the simulated futures end above {usd(p50, lang)}. In the worst 5% you end with "
                 f"{usd(p5, lang)} or less. Probability of ending below your reference point "
                 f"({usd(W_ref, lang)}): {below:.0%}.")
        else:
            s = (f"La mitad de los futuros simulados termina con más de {usd(p50)}. En el 5% más malo terminas con "
                 f"{usd(p5)} o menos. Probabilidad de terminar por debajo de tu punto de referencia "
                 f"({usd(W_ref)}): {below:.0%}.")
        if name != reference:
            diff = np.median(wt) - np.median(ref)
            win = (wt > ref + 1e-6).mean()
            if np.allclose(wt, ref):
                s += (f" It gives exactly the same result as «{rname}»." if lang == "en" else
                      f" Da exactamente lo mismo que «{rname}».")
            elif abs(diff) < 0.005 * np.median(ref):
                s += (f" Its typical result is practically the same as with «{rname}»." if lang == "en" else
                      f" Su resultado típico es prácticamente el mismo que con «{rname}».")
            elif lang == "en":
                s += (f" Compared with «{rname}», your typical result {'rises' if diff >= 0 else 'falls'} "
                      f"{usd(abs(diff), lang)}, and you beat it in {win:.0%} of the scenarios.")
            else:
                s += (f" Frente a «{rname}», tu resultado típico {'sube' if diff >= 0 else 'baja'} "
                      f"{usd(abs(diff))}, y le ganas en {win:.0%} de los escenarios.")
        out[name] = s
    return out
