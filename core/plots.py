"""Gráficos compartidos por el notebook y la app."""
import numpy as np
import plotly.graph_objects as go
from .evaluation import fan_quantiles

COLORS = {
    "Rebalanceo por bandas": "#1f77b4", "Tú tal como eres": "#d62728", "Comprar y mantener": "#7f7f7f",
    "Re-optimización anual": "#2ca02c", "Venta por pánico": "#ff7f0e", "Persecución de rendimiento": "#9467bd",
}


def _rgba(hex_color, a):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a})"


def fan_figure(results, names, W_ref=None, title="Riqueza simulada a 10 años"):
    fig = go.Figure()
    for name in names:
        q = fan_quantiles(results[name])
        x = q.index.to_numpy() / 12
        c = COLORS.get(name, "#1f77b4")
        for lo, hi, a in ((5, 95, 0.12), (25, 75, 0.28)):
            fig.add_trace(go.Scatter(
                x=np.concatenate([x, x[::-1]]), y=np.concatenate([q[hi].to_numpy(), q[lo].to_numpy()[::-1]]),
                fill="toself", fillcolor=_rgba(c, a), line=dict(width=0), hoverinfo="skip",
                name=f"{name}: {lo}–{hi}% de los escenarios"))
        fig.add_trace(go.Scatter(x=x, y=q[50], line=dict(color=c, width=3), name=f"{name}: mediana"))
    if W_ref is not None:
        fig.add_hline(y=W_ref, line_dash="dot", annotation_text="Punto de referencia")
    fig.update_layout(title=title, xaxis_title="Años", yaxis_title="Riqueza (US$)", template="plotly_white",
                      hovermode="x unified", height=500, legend=dict(orientation="h", y=-0.2))
    return fig


def terminal_figure(results, title="Riqueza final por política"):
    fig = go.Figure()
    for name, res in results.items():
        fig.add_trace(go.Box(y=res.terminal, name=name, marker_color=COLORS.get(name), boxmean=True))
    fig.update_layout(title=title, yaxis_title="Riqueza final (US$)", template="plotly_white",
                      showlegend=False, height=450)
    return fig
