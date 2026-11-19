"""Dashboard de portafolio conductual: perfil → portafolio → futuro simulado → costo de los sesgos."""
import json
from dataclasses import replace

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from core import profile as qp
from core.data import UNIVERSE, CASH, load_returns
from core.portfolio import Constraints, build_portfolio, class_matrix
from core.scenarios import block_bootstrap, EVAL_SEED
from core.policies import standard_policies, BH, PFA, CFA, PANIC, CHASE, CLIENT
from core.evaluation import evaluate, results_table, behavior_costs, plain_language, recommend, usd
from core.plots import fan_figure, terminal_figure

APP_SCEN = 500
COST = 0.001

st.set_page_config(page_title="Tu plan de inversión", layout="wide")


@st.cache_data
def load_inputs():
    rets = load_returns("data/monthly_returns.csv")
    with open("data/tuned_params.json", encoding="utf-8") as fh:
        tuned = json.load(fh)
    return rets, tuned


rets, tuned = load_inputs()
tickers = list(rets.columns)
hist = rets.to_numpy(float)
cash_idx = tickers.index(CASH)
A = class_matrix(tickers, UNIVERSE)[0]


@st.cache_data(show_spinner="Optimizando tu portafolio con Gurobi…")
def cached_portfolio(lam, K, l, u, cap):
    return build_portfolio(lam, rets, Constraints(K=K, l=l, u=u, class_cap=cap))


@st.cache_data(show_spinner="Simulando 500 futuros posibles…")
def cached_results(w_star, prof_items, b, W0, include_cfa, theta, window, K, l, u, cap):
    prof = qp.Profile(**dict(prof_items))
    sc = block_bootstrap(hist, APP_SCEN, seed=EVAL_SEED)
    cfa = None
    if include_cfa:
        cfa = dict(theta=theta, window=window, cons=Constraints(K=K, l=l, u=u, class_cap=cap), A=A, hist=hist)
    pols = standard_policies(prof, np.array(w_star), b, cash_idx, cfa=cfa)
    return evaluate(pols, sc, hist, W0=W0, cost=COST)


if "answers" not in st.session_state:
    st.session_state.answers = dict(qp.DEFAULT_ANSWERS)

# ---------------- Barra lateral ----------------
with st.sidebar:
    st.header("Tus datos")
    W0 = float(st.number_input("Riqueza inicial (US$)", min_value=1_000, max_value=100_000_000,
                               value=100_000, step=5_000))
    use_goal = st.checkbox("Medir el éxito contra una meta de crecimiento")
    g = st.slider("Meta de crecimiento anual (%)", 0.0, 10.0, 4.0, 0.5, disabled=not use_goal) / 100
    W_ref = W0 * (1 + g) ** 10 if use_goal else W0

    st.header("Reglas del asesor")
    K = st.slider("Máximo de activos (K)", 3, 15, 8)
    l = st.slider("Posición mínima por activo (%)", 1, 10, 5) / 100
    u = st.slider("Posición máxima por activo (%)", 15, 60, 35) / 100
    cap = st.slider("Tope por clase de activo (%)", 30, 100, 50) / 100
    if K * u < 1:
        st.error("Con estos valores no se puede invertir el 100%: aumenta K o la posición máxima.")
        st.stop()

    with st.expander("Ajustar el perfil a mano (asesor)"):
        override = st.checkbox("Sobrescribir λ, α y β estimados")
        lam_o = st.slider("λ: aversión a pérdidas", 1.0, 5.0, 2.25, 0.05)
        a_o = st.slider("α: curvatura en ganancias", 0.2, 1.0, 0.88, 0.01)
        b_o = st.slider("β: curvatura en pérdidas", 0.2, 1.0, 0.88, 0.01)

p = qp.estimate_profile(st.session_state.answers)
if override:
    p = replace(p, lam=lam_o, alpha=a_o, beta=b_o)

with st.sidebar.expander("Sesgos: escenarios hipotéticos (asesor)"):
    bias_override = st.checkbox("Modificar los sesgos del perfil")
    panic_o = st.checkbox("Vende en pánico", value=p.panic)
    d_o = st.slider("Caída que dispara la venta (%)", 5, 40, int(round(p.d * 100))) / 100
    r_o = st.slider("Rebote para volver a invertir (%)", 0, 40, int(round(p.r * 100))) / 100
    phi_o = st.slider("Fracción que vende (%)", 10, 100, int(round(p.phi * 100)), 10) / 100
    chase_o = st.checkbox("Persigue rendimientos", value=p.chase)
    kappa_o = st.slider("Fracción que mueve a los ganadores (%)", 0, 100, int(round(p.kappa * 100)), 5) / 100
    f_opts = [1, 3, 6, 12]
    f_o = st.selectbox("Cada cuántos meses persigue", f_opts, index=f_opts.index(p.f) if p.f in f_opts else 1)
if bias_override:
    p = replace(p, panic=panic_o, d=d_o, r=r_o, phi=phi_o, chase=chase_o and kappa_o > 0,
                kappa=kappa_o if kappa_o > 0 else p.kappa, f=int(f_o))

st.title("Tu plan de inversión")
st.caption("Herramienta educativa: los resultados son simulaciones con datos históricos 2008–2026, no promesas.")
tab1, tab2, tab3, tab4 = st.tabs(["1. Cuestionario", "2. Mi portafolio", "3. Mi futuro", "4. Comparar reglas"])

# ---------------- 1. Cuestionario ----------------
with tab1:
    st.subheader("Cuestionario (11 preguntas)")
    st.write("No hay respuestas correctas. Responde pensando en tu propio dinero.")
    saved = st.session_state.answers
    with st.form("quiz"):
        ans = {}
        st.markdown("#### Apuestas con ganancias y pérdidas")
        for q in qp.LAMBDA_QUESTIONS:
            opts = qp.lambda_options(q["loss"])
            labels = [o[0] for o in opts]
            idx = next((i for i, o in enumerate(opts) if o[1] == saved.get(q["id"])), 2)
            choice = st.radio(qp.lambda_text(q["loss"]), labels, index=idx)
            ans[q["id"]] = opts[labels.index(choice)][1]
        st.markdown("#### Ganancias seguras o apuestas")
        for q in qp.ALPHA_QUESTIONS:
            ans[q["id"]] = st.slider(qp.alpha_text(q["stake"]), 0.0, float(q["stake"]),
                                     float(saved[q["id"]]), 0.5, format="%.1f%%")
        st.markdown("#### Pérdidas seguras o apuestas")
        for q in qp.BETA_QUESTIONS:
            ans[q["id"]] = st.slider(qp.beta_text(q["stake"]), 0.0, float(q["stake"]),
                                     float(saved[q["id"]]), 0.5, format="%.1f%%")
        st.markdown("#### ¿Qué harías?")
        for q in qp.BIAS_QUESTIONS:
            choice = st.radio(q["text"], q["options"], index=int(saved[q["id"]]))
            ans[q["id"]] = q["options"].index(choice)
        if st.form_submit_button("Calcular mi perfil", type="primary"):
            st.session_state.answers = ans
            st.rerun()

    st.subheader("Tu perfil")
    c1, c2, c3 = st.columns(3)
    c1.metric("Aversión a pérdidas λ", f"{p.lam:.2f}")
    c2.metric("Curvatura en ganancias α", f"{p.alpha:.2f}")
    c3.metric("Curvatura en pérdidas β", f"{p.beta:.2f}")
    for line in qp.describe_profile(p):
        st.markdown(f"- {line}")
    if not np.isnan(p.lam_curv):
        st.caption(f"λ corregido por la curvatura de tus respuestas: {p.lam_curv:.2f} (informativo).")

# ---------------- Cálculos ----------------
port = cached_portfolio(p.lam, K, l, u, cap)
w_star = port.weights.to_numpy()
include_cfa = st.session_state.get("cfa", False)
res = cached_results(tuple(np.round(w_star, 10)), tuple(sorted(p.as_dict().items())), float(tuned["b_star"]),
                     W0, include_cfa, float(tuned["theta_star"]), int(tuned["window_star"]), K, l, u, cap)
b_star = float(tuned["b_star"])
candidates = [BH, PFA] + ([CFA] if include_cfa else [])
rec = recommend(res, p, W0, W_ref, candidates)
HOW_TO = {
    BH: "**Cómo mantenerlo:** compra hoy estos montos y mantenlos. En las simulaciones, rebalancear no mejoró "
        "tu resultado, así que no necesitas operar cada mes. Revisa tu plan una vez al año o si cambian tus metas.",
    PFA: f"**Cómo mantenerlo:** revisa tu portafolio una vez al mes. Si algún activo se aleja más de "
         f"{b_star:.1%} de su peso objetivo, vuelve a los pesos de esta tabla. Si no, no hagas nada.",
    CFA: "**Cómo mantenerlo:** una vez al año, vuelve a calcular el portafolio con los datos más recientes "
         "(esta app lo hace por ti) y ajusta tus posiciones a la nueva tabla.",
}

# ---------------- 2. Mi portafolio ----------------
with tab2:
    st.subheader("Tu decisión de hoy: qué comprar")
    c1, c2, c3 = st.columns(3)
    c1.metric("Activos en el portafolio", int((w_star > 0).sum()))
    c2.metric("Retorno anual esperado (histórico)", f"{(1 + port.mean) ** 12 - 1:.1%}")
    c3.metric("Pérdida promedio en el peor 5% de los meses", f"{port.cvar:.1%}")
    st.caption(f"Tu límite de pérdida en meses malos (CVaR 95%) es {port.cvar_limit:.1%} al mes; lo fija tu aversión "
               f"a pérdidas λ = {p.lam:.2f}. Estado del optimizador: {port.status}.")
    tbl = port.table(W0)
    left, right = st.columns([3, 2])
    left.dataframe(tbl.style.format({"Peso": "{:.1%}", "Monto a invertir (US$)": "{:,.0f}"}),
                   use_container_width=True)
    by_class = tbl.groupby("Clase", as_index=False)["Peso"].sum()
    right.plotly_chart(px.pie(by_class, names="Clase", values="Peso", hole=0.5, title="Por clase de activo"),
                       use_container_width=True)
    st.info(HOW_TO[rec["chosen"]])

# ---------------- 3. Mi futuro ----------------
with tab3:
    st.subheader("500 futuros posibles para tu dinero")
    st.plotly_chart(fan_figure(res, [PFA, CLIENT], W_ref=W_ref,
                               title="Con disciplina (azul) y tal como eres (rojo)"), use_container_width=True)
    st.markdown("La línea gruesa es el resultado **típico** (la mitad de los escenarios termina por encima). "
                "La banda oscura contiene la mitad central de los escenarios y la banda clara, el 90%.")
    if np.allclose(res[CLIENT].terminal, res[PFA].terminal):
        st.success("No detectamos sesgos: tu comportamiento coincide con la regla disciplinada.")

# ---------------- 4. Comparar reglas ----------------
with tab4:
    st.subheader("Nuestra recomendación")
    st.success(f"**{rec['chosen']}**: {rec['reason']}.")
    if not include_cfa:
        if st.button("Incluir también la re-optimización anual (puede tardar 2–5 minutos)"):
            st.session_state.cfa = True
            st.rerun()

    st.subheader("¿Cuánto te cuesta tu comportamiento?")
    bc = behavior_costs(res, reference=PFA)
    cols = st.columns(len(bc))
    flags = {PANIC: p.panic, CHASE: p.chase, CLIENT: p.panic or p.chase}
    for col, (name, row) in zip(cols, bc.iterrows()):
        label = name if flags.get(name, True) else f"{name} (hipotético)"
        col.metric(label, usd(-row["Costo en la mediana (US$)"]),
                   help=f"Cambio en tu riqueza final típica frente a «{PFA}». Peor que la disciplina en "
                        f"{row['Escenarios peores que la disciplina']:.0%} de los escenarios.")
    st.caption("Un número negativo es dinero que pierdes, en el resultado típico a 10 años, por actuar así en vez de "
               "seguir la regla de bandas. «Hipotético» significa que no detectamos ese sesgo en tus respuestas.")

    st.subheader("Las reglas en palabras simples")
    for name, sentence in plain_language(res, W0, W_ref, reference=PFA).items():
        st.markdown(f"**{name}.** {sentence}")

    st.plotly_chart(terminal_figure(res), use_container_width=True)

    st.subheader("¿Cuándo cambiaría la recomendación?")
    st.markdown(
        "- **Si tus costos de transacción suben mucho**, la regla de no operar (comprar y mantener) gana terreno.\n"
        "- **Si cambia tu aversión a pérdidas**, cambia tu portafolio: vuelve a responder el cuestionario.\n"
        "- **Si no puedes seguir la regla en las caídas**, lo más importante es la disciplina: el costo de los "
        "sesgos suele ser mayor que la diferencia entre reglas.\n"
        "- **Si cambia el mercado** respecto de 2008–2026, el asesor debe volver a ajustar los parámetros.")

    with st.expander("Detalle estadístico (para el asesor)"):
        st.dataframe(results_table(res, p, W0, W_ref), use_container_width=True)
