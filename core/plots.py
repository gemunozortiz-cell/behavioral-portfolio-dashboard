"""Gráficos compartidos por el notebook y la app (en español o inglés)."""
import numpy as np
import plotly.graph_objects as go
from .evaluation import fan_quantiles
from .i18n import policy_name

COLORS = {
    "Rebalanceo por bandas": "#1f77b4", "Tú tal como eres": "#d62728", "Comprar y mantener": "#7f7f7f",
    "Re-optimización anual": "#2ca02c", "Venta por pánico": "#ff7f0e", "Persecución de rendimiento": "#9467bd",
}
LABELS = {
    "es": {"band": "{name}: {lo}–{hi}% de los escenarios", "median": "{name}: mediana", "ref": "Punto de referencia",
           "years": "Años", "wealth": "Riqueza (US$)", "final": "Riqueza final (US$)",
           "fan_title": "Riqueza simulada a 10 años", "box_title": "Riqueza final por política"},
    "en": {"band": "{name}: {lo}–{hi}% of scenarios", "median": "{name}: median", "ref": "Reference point",
           "years": "Years", "wealth": "Wealth (US$)", "final": "Final wealth (US$)",
           "fan_title": "Simulated wealth over 10 years", "box_title": "Final wealth by policy"},
}


def _rgba(hex_color, a):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a})"


def fan_figure(results, names, W_ref=None, title=None, lang="es"):
    L = LABELS[lang]
    fig = go.Figure()
    for name in names:
        q = fan_quantiles(results[name])
        x = q.index.to_numpy() / 12
        c = COLORS.get(name, "#1f77b4")
        shown = policy_name(name, lang)
        for lo, hi, a in ((5, 95, 0.12), (25, 75, 0.28)):
            fig.add_trace(go.Scatter(
                x=np.concatenate([x, x[::-1]]), y=np.concatenate([q[hi].to_numpy(), q[lo].to_numpy()[::-1]]),
                fill="toself", fillcolor=_rgba(c, a), line=dict(width=0), hoverinfo="skip",
                name=L["band"].format(name=shown, lo=lo, hi=hi)))
        fig.add_trace(go.Scatter(x=x, y=q[50], line=dict(color=c, width=3), name=L["median"].format(name=shown)))
    if W_ref is not None:
        fig.add_hline(y=W_ref, line_dash="dot", annotation_text=L["ref"])
    fig.update_layout(title=title or L["fan_title"], xaxis_title=L["years"], yaxis_title=L["wealth"],
                      template="plotly_white", hovermode="x unified", height=500,
                      legend=dict(orientation="h", y=-0.2))
    return fig


def terminal_figure(results, title=None, lang="es"):
    L = LABELS[lang]
    fig = go.Figure()
    for name, res in results.items():
        fig.add_trace(go.Box(y=res.terminal, name=policy_name(name, lang), marker_color=COLORS.get(name),
                             boxmean=True))
    fig.update_layout(title=title or L["box_title"], yaxis_title=L["final"], template="plotly_white",
                      showlegend=False, height=450)
    return fig
