"""Dashboard de portafolio conductual: perfil → portafolio → futuro simulado → costo de los sesgos.
Bilingüe: español / English (selector en la barra lateral o ?lang=en en la URL)."""
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
from core.i18n import LANGS, policy_name, klass_name, class_name, asset_name

APP_SCEN = 500
COST = 0.001

# ---------------- Textos / Texts ----------------
TXT = {
    "es": {
        "page": "Tu plan de inversión",
        "lang": "Idioma / Language",
        "spin_opt": "Optimizando tu portafolio con Gurobi…",
        "spin_sim": "Simulando 500 futuros posibles…",
        "your_data": "Tus datos",
        "w0": "Riqueza inicial (US$)",
        "use_goal": "Medir el éxito contra una meta de crecimiento",
        "goal": "Meta de crecimiento anual (%)",
        "rules": "Reglas del asesor",
        "K": "Máximo de activos (K)",
        "l": "Posición mínima por activo (%)",
        "u": "Posición máxima por activo (%)",
        "cap": "Tope por clase de activo (%)",
        "infeasible": "Con estos valores no se puede invertir el 100%: aumenta K o la posición máxima.",
        "manual": "Ajustar el perfil a mano (asesor)",
        "override": "Sobrescribir λ, α y β estimados",
        "lam": "λ: aversión a pérdidas",
        "alpha": "α: curvatura en ganancias",
        "beta": "β: curvatura en pérdidas",
        "bias_box": "Sesgos: escenarios hipotéticos (asesor)",
        "bias_override": "Modificar los sesgos del perfil",
        "panic": "Vende en pánico",
        "d": "Caída que dispara la venta (%)",
        "r": "Rebote para volver a invertir (%)",
        "phi": "Fracción que vende (%)",
        "chase": "Persigue rendimientos",
        "kappa": "Fracción que mueve a los ganadores (%)",
        "f": "Cada cuántos meses persigue",
        "caption": "Herramienta educativa: los resultados son simulaciones con datos históricos 2008–2026, no promesas.",
        "tabs": ["1. Cuestionario", "2. Mi portafolio", "3. Mi futuro", "4. Comparar reglas"],
        "quiz": "Cuestionario (11 preguntas)",
        "quiz_intro": "No hay respuestas correctas. Responde pensando en tu propio dinero.",
        "q_lam": "Apuestas con ganancias y pérdidas",
        "q_alpha": "Ganancias seguras o apuestas",
        "q_beta": "Pérdidas seguras o apuestas",
        "q_bias": "¿Qué harías?",
        "submit": "Calcular mi perfil",
        "profile": "Tu perfil",
        "m_lam": "Aversión a pérdidas λ",
        "m_alpha": "Curvatura en ganancias α",
        "m_beta": "Curvatura en pérdidas β",
        "lam_curv": "λ corregido por la curvatura de tus respuestas: {v:.2f} (informativo).",
        "how_bh": "**Cómo mantenerlo:** compra hoy estos montos y mantenlos. En las simulaciones, rebalancear no mejoró "
                  "tu resultado, así que no necesitas operar cada mes. Revisa tu plan una vez al año o si cambian tus metas.",
        "how_pfa": "**Cómo mantenerlo:** revisa tu portafolio una vez al mes. Si algún activo se aleja más de "
                   "{b:.1%} de su peso objetivo, vuelve a los pesos de esta tabla. Si no, no hagas nada.",
        "how_cfa": "**Cómo mantenerlo:** una vez al año, vuelve a calcular el portafolio con los datos más recientes "
                   "(esta app lo hace por ti) y ajusta tus posiciones a la nueva tabla.",
        "today": "Tu decisión de hoy: qué comprar",
        "n_assets": "Activos en el portafolio",
        "exp_ret": "Retorno anual esperado (histórico)",
        "cvar": "Pérdida promedio en el peor 5% de los meses",
        "cvar_cap": "Tu límite de pérdida en meses malos (CVaR 95%) es {lim:.1%} al mes; lo fija tu aversión "
                    "a pérdidas λ = {lam:.2f}. Estado del optimizador: {status}.",
        "col_name": "Nombre", "col_class": "Clase", "col_w": "Peso", "col_amt": "Monto a invertir (US$)",
        "by_class": "Por clase de activo",
        "futures": "500 futuros posibles para tu dinero",
        "fan_title": "Con disciplina (azul) y tal como eres (rojo)",
        "fan_help": "La línea gruesa es el resultado **típico** (la mitad de los escenarios termina por encima). "
                    "La banda oscura contiene la mitad central de los escenarios y la banda clara, el 90%.",
        "no_bias": "No detectamos sesgos: tu comportamiento coincide con la regla disciplinada.",
        "rec": "Nuestra recomendación",
        "cfa_btn": "Incluir también la re-optimización anual (puede tardar 2–5 minutos)",
        "cost_title": "¿Cuánto te cuesta tu comportamiento?",
        "hyp": "(hipotético)",
        "cost_help": "Cambio en tu riqueza final típica frente a «{ref}». Peor que la disciplina en "
                     "{pct:.0%} de los escenarios.",
        "cost_cap": "Un número negativo es dinero que pierdes, en el resultado típico a 10 años, por actuar así en vez de "
                    "seguir la regla de bandas. «Hipotético» significa que no detectamos ese sesgo en tus respuestas.",
        "plain": "Las reglas en palabras simples",
        "when": "¿Cuándo cambiaría la recomendación?",
        "when_md": "- **Si tus costos de transacción suben mucho**, la regla de no operar (comprar y mantener) gana terreno.\n"
                   "- **Si cambia tu aversión a pérdidas**, cambia tu portafolio: vuelve a responder el cuestionario.\n"
                   "- **Si no puedes seguir la regla en las caídas**, lo más importante es la disciplina: el costo de los "
                   "sesgos suele ser mayor que la diferencia entre reglas.\n"
                   "- **Si cambia el mercado** respecto de 2008–2026, el asesor debe volver a ajustar los parámetros.",
        "detail": "Detalle estadístico (para el asesor)",
    },
    "en": {
        "page": "Your investment plan",
        "lang": "Idioma / Language",
        "spin_opt": "Optimizing your portfolio with Gurobi…",
        "spin_sim": "Simulating 500 possible futures…",
        "your_data": "Your data",
        "w0": "Initial wealth (US$)",
        "use_goal": "Measure success against a growth goal",
        "goal": "Annual growth goal (%)",
        "rules": "Advisor's rules",
        "K": "Maximum number of assets (K)",
        "l": "Minimum position per asset (%)",
        "u": "Maximum position per asset (%)",
        "cap": "Cap per asset class (%)",
        "infeasible": "With these values it is impossible to invest 100%: increase K or the maximum position.",
        "manual": "Adjust the profile by hand (advisor)",
        "override": "Override the estimated λ, α and β",
        "lam": "λ: loss aversion",
        "alpha": "α: curvature for gains",
        "beta": "β: curvature for losses",
        "bias_box": "Biases: what-if scenarios (advisor)",
        "bias_override": "Change the profile's biases",
        "panic": "Panic-sells",
        "d": "Drop that triggers the sale (%)",
        "r": "Rebound needed to invest again (%)",
        "phi": "Fraction sold (%)",
        "chase": "Chases performance",
        "kappa": "Fraction moved into the winners (%)",
        "f": "Every how many months it chases",
        "caption": "Educational tool: results are simulations based on 2008–2026 historical data, not promises.",
        "tabs": ["1. Questionnaire", "2. My portfolio", "3. My future", "4. Compare rules"],
        "quiz": "Questionnaire (11 questions)",
        "quiz_intro": "There are no right answers. Answer thinking about your own money.",
        "q_lam": "Bets with gains and losses",
        "q_alpha": "Sure gains or bets",
        "q_beta": "Sure losses or bets",
        "q_bias": "What would you do?",
        "submit": "Compute my profile",
        "profile": "Your profile",
        "m_lam": "Loss aversion λ",
        "m_alpha": "Curvature for gains α",
        "m_beta": "Curvature for losses β",
        "lam_curv": "λ corrected for the curvature of your answers: {v:.2f} (for information).",
        "how_bh": "**How to keep it:** buy these amounts today and hold them. In the simulations, rebalancing did not "
                  "improve your result, so you don't need to trade every month. Review your plan once a year or if "
                  "your goals change.",
        "how_pfa": "**How to keep it:** check your portfolio once a month. If any asset drifts more than {b:.1%} from "
                   "its target weight, go back to the weights in this table. Otherwise, do nothing.",
        "how_cfa": "**How to keep it:** once a year, recompute the portfolio with the latest data (this app does it "
                   "for you) and adjust your positions to the new table.",
        "today": "Today's decision: what to buy",
        "n_assets": "Assets in the portfolio",
        "exp_ret": "Expected annual return (historical)",
        "cvar": "Average loss in the worst 5% of months",
        "cvar_cap": "Your loss limit for bad months (CVaR 95%) is {lim:.1%} per month; it is set by your loss "
                    "aversion λ = {lam:.2f}. Optimizer status: {status}.",
        "col_name": "Name", "col_class": "Class", "col_w": "Weight", "col_amt": "Amount to invest (US$)",
        "by_class": "By asset class",
        "futures": "500 possible futures for your money",
        "fan_title": "With discipline (blue) and as you are (red)",
        "fan_help": "The thick line is the **typical** result (half of the scenarios end above it). "
                    "The dark band holds the middle half of the scenarios and the light band, 90%.",
        "no_bias": "No biases detected: your behavior matches the disciplined rule.",
        "rec": "Our recommendation",
        "cfa_btn": "Also include annual re-optimization (may take 2–5 minutes)",
        "cost_title": "How much does your behavior cost you?",
        "hyp": "(hypothetical)",
        "cost_help": "Change in your typical final wealth compared with «{ref}». Worse than discipline in "
                     "{pct:.0%} of the scenarios.",
        "cost_cap": "A negative number is money you lose, in the typical 10-year result, by acting this way instead of "
                    "following the band rule. «Hypothetical» means we did not detect that bias in your answers.",
        "plain": "The rules in plain words",
        "when": "When would the recommendation change?",
        "when_md": "- **If your transaction costs rise a lot**, the no-trading rule (buy and hold) gains ground.\n"
                   "- **If your loss aversion changes**, your portfolio changes: answer the questionnaire again.\n"
                   "- **If you cannot follow the rule during drops**, discipline matters most: the cost of the biases "
                   "is usually larger than the difference between rules.\n"
                   "- **If the market changes** compared with 2008–2026, the advisor should re-tune the parameters.",
        "detail": "Statistical detail (for the advisor)",
    },
}
STATUS_EN = {"óptimo": "optimal"}
RESULT_COLS_EN = {
    "Clase": "Class", "Valor PT medio": "Mean PT value", "Valor PT desv.": "PT value std.",
    "Valor PT P5": "PT value P5", "Valor PT P95": "PT value P95", "IC95% PT (normal)": "95% CI PT (normal)",
    "IC95% PT (bootstrap)": "95% CI PT (bootstrap)", "Equivalente cierto (US$)": "Certainty equivalent (US$)",
    "Riqueza final media": "Mean final wealth", "Riqueza desv.": "Wealth std.", "Riqueza P5": "Wealth P5",
    "Riqueza P50": "Wealth P50", "Riqueza P95": "Wealth P95", "IC95% riqueza media": "95% CI mean wealth",
    "Caída máx. mediana": "Median max. drawdown", "Costos medios": "Mean costs",
    "Rotación anual media": "Mean annual turnover",
}

# ---------------- Idioma / Language ----------------
if "lang" not in st.session_state:
    q = st.query_params.get("lang", "es")
    st.session_state.lang = q if q in LANGS else "es"
lang = st.session_state.lang
t = TXT[lang]

st.set_page_config(page_title=t["page"], layout="wide")


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


@st.cache_data(show_spinner=False)
def cached_portfolio(lam, K, l, u, cap):
    return build_portfolio(lam, rets, Constraints(K=K, l=l, u=u, class_cap=cap))


@st.cache_data(show_spinner=False)
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

# ---------------- Barra lateral / Sidebar ----------------
with st.sidebar:
    new_lang = st.radio(t["lang"], list(LANGS), index=list(LANGS).index(lang), format_func=LANGS.get,
                        horizontal=True)
    if new_lang != lang:
        st.session_state.lang = new_lang
        st.query_params["lang"] = new_lang
        st.rerun()

    st.header(t["your_data"])
    W0 = float(st.number_input(t["w0"], min_value=1_000, max_value=100_000_000, value=100_000, step=5_000))
    use_goal = st.checkbox(t["use_goal"])
    g = st.slider(t["goal"], 0.0, 10.0, 4.0, 0.5, disabled=not use_goal) / 100
    W_ref = W0 * (1 + g) ** 10 if use_goal else W0

    st.header(t["rules"])
    K = st.slider(t["K"], 3, 15, 8)
    l = st.slider(t["l"], 1, 10, 5) / 100
    u = st.slider(t["u"], 15, 60, 35) / 100
    cap = st.slider(t["cap"], 30, 100, 50) / 100
    if K * u < 1:
        st.error(t["infeasible"])
        st.stop()

    with st.expander(t["manual"]):
        override = st.checkbox(t["override"])
        lam_o = st.slider(t["lam"], 1.0, 5.0, 2.25, 0.05)
        a_o = st.slider(t["alpha"], 0.2, 1.0, 0.88, 0.01)
        b_o = st.slider(t["beta"], 0.2, 1.0, 0.88, 0.01)

p = qp.estimate_profile(st.session_state.answers)
if override:
    p = replace(p, lam=lam_o, alpha=a_o, beta=b_o)

with st.sidebar.expander(t["bias_box"]):
    bias_override = st.checkbox(t["bias_override"])
    panic_o = st.checkbox(t["panic"], value=p.panic)
    d_o = st.slider(t["d"], 5, 40, int(round(p.d * 100))) / 100
    r_o = st.slider(t["r"], 0, 40, int(round(p.r * 100))) / 100
    phi_o = st.slider(t["phi"], 10, 100, int(round(p.phi * 100)), 10) / 100
    chase_o = st.checkbox(t["chase"], value=p.chase)
    kappa_o = st.slider(t["kappa"], 0, 100, int(round(p.kappa * 100)), 5) / 100
    f_opts = [1, 3, 6, 12]
    f_o = st.selectbox(t["f"], f_opts, index=f_opts.index(p.f) if p.f in f_opts else 1)
if bias_override:
    p = replace(p, panic=panic_o, d=d_o, r=r_o, phi=phi_o, chase=chase_o and kappa_o > 0,
                kappa=kappa_o if kappa_o > 0 else p.kappa, f=int(f_o))

st.title(t["page"])
st.caption(t["caption"])
tab1, tab2, tab3, tab4 = st.tabs(t["tabs"])

# ---------------- 1. Cuestionario / Questionnaire ----------------
with tab1:
    st.subheader(t["quiz"])
    st.write(t["quiz_intro"])
    saved = st.session_state.answers
    with st.form("quiz"):
        ans = {}
        st.markdown(f"#### {t['q_lam']}")
        for q in qp.LAMBDA_QUESTIONS:
            opts = qp.lambda_options(q["loss"], lang)
            labels = [o[0] for o in opts]
            idx = next((i for i, o in enumerate(opts) if o[1] == saved.get(q["id"])), 2)
            choice = st.radio(qp.lambda_text(q["loss"], lang), labels, index=idx)
            ans[q["id"]] = opts[labels.index(choice)][1]
        st.markdown(f"#### {t['q_alpha']}")
        for q in qp.ALPHA_QUESTIONS:
            ans[q["id"]] = st.slider(qp.alpha_text(q["stake"], lang), 0.0, float(q["stake"]),
                                     float(saved[q["id"]]), 0.5, format="%.1f%%")
        st.markdown(f"#### {t['q_beta']}")
        for q in qp.BETA_QUESTIONS:
            ans[q["id"]] = st.slider(qp.beta_text(q["stake"], lang), 0.0, float(q["stake"]),
                                     float(saved[q["id"]]), 0.5, format="%.1f%%")
        st.markdown(f"#### {t['q_bias']}")
        for q in qp.bias_questions(lang):
            choice = st.radio(q["text"], q["options"], index=int(saved[q["id"]]))
            ans[q["id"]] = q["options"].index(choice)
        if st.form_submit_button(t["submit"], type="primary"):
            st.session_state.answers = ans
            st.rerun()

    st.subheader(t["profile"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t["m_lam"], f"{p.lam:.2f}")
    c2.metric(t["m_alpha"], f"{p.alpha:.2f}")
    c3.metric(t["m_beta"], f"{p.beta:.2f}")
    for line in qp.describe_profile(p, lang):
        st.markdown(f"- {line}")
    if not np.isnan(p.lam_curv):
        st.caption(t["lam_curv"].format(v=p.lam_curv))

# ---------------- Cálculos / Computations ----------------
with st.spinner(t["spin_opt"]):
    port = cached_portfolio(p.lam, K, l, u, cap)
w_star = port.weights.to_numpy()
include_cfa = st.session_state.get("cfa", False)
with st.spinner(t["spin_sim"]):
    res = cached_results(tuple(np.round(w_star, 10)), tuple(sorted(p.as_dict().items())), float(tuned["b_star"]),
                         W0, include_cfa, float(tuned["theta_star"]), int(tuned["window_star"]), K, l, u, cap)
b_star = float(tuned["b_star"])
candidates = [BH, PFA] + ([CFA] if include_cfa else [])
rec = recommend(res, p, W0, W_ref, candidates, lang=lang)
HOW_TO = {BH: t["how_bh"], PFA: t["how_pfa"].format(b=b_star), CFA: t["how_cfa"]}

# ---------------- 2. Mi portafolio / My portfolio ----------------
with tab2:
    st.subheader(t["today"])
    c1, c2, c3 = st.columns(3)
    c1.metric(t["n_assets"], int((w_star > 0).sum()))
    c2.metric(t["exp_ret"], f"{(1 + port.mean) ** 12 - 1:.1%}")
    c3.metric(t["cvar"], f"{port.cvar:.1%}")
    status = STATUS_EN.get(port.status, port.status) if lang == "en" else port.status
    st.caption(t["cvar_cap"].format(lim=port.cvar_limit, lam=p.lam, status=status))
    tbl = port.table(W0)
    tbl = pd.DataFrame({
        t["col_name"]: [asset_name(tk, lang) for tk in tbl.index],
        t["col_class"]: [class_name(c, lang) for c in tbl["Clase"]],
        t["col_w"]: tbl["Peso"].to_numpy(),
        t["col_amt"]: tbl["Monto a invertir (US$)"].to_numpy(),
    }, index=tbl.index)
    left, right = st.columns([3, 2])
    left.dataframe(tbl.style.format({t["col_w"]: "{:.1%}", t["col_amt"]: "{:,.0f}"}), width="stretch")
    by_class = tbl.groupby(t["col_class"], as_index=False)[t["col_w"]].sum()
    right.plotly_chart(px.pie(by_class, names=t["col_class"], values=t["col_w"], hole=0.5, title=t["by_class"]),
                       width="stretch")
    st.info(HOW_TO[rec["chosen"]])

# ---------------- 3. Mi futuro / My future ----------------
with tab3:
    st.subheader(t["futures"])
    st.plotly_chart(fan_figure(res, [PFA, CLIENT], W_ref=W_ref, title=t["fan_title"], lang=lang),
                    width="stretch")
    st.markdown(t["fan_help"])
    if np.allclose(res[CLIENT].terminal, res[PFA].terminal):
        st.success(t["no_bias"])

# ---------------- 4. Comparar reglas / Compare rules ----------------
with tab4:
    st.subheader(t["rec"])
    st.success(f"**{policy_name(rec['chosen'], lang)}**: {rec['reason']}.")
    if not include_cfa:
        if st.button(t["cfa_btn"]):
            st.session_state.cfa = True
            st.rerun()

    st.subheader(t["cost_title"])
    bc = behavior_costs(res, reference=PFA)
    cols = st.columns(len(bc))
    flags = {PANIC: p.panic, CHASE: p.chase, CLIENT: p.panic or p.chase}
    for col, (name, row) in zip(cols, bc.iterrows()):
        shown = policy_name(name, lang)
        label = shown if flags.get(name, True) else f"{shown} {t['hyp']}"
        col.metric(label, usd(-row["Costo en la mediana (US$)"], lang),
                   help=t["cost_help"].format(ref=policy_name(PFA, lang),
                                              pct=row["Escenarios peores que la disciplina"]))
    st.caption(t["cost_cap"])

    st.subheader(t["plain"])
    for name, sentence in plain_language(res, W0, W_ref, reference=PFA, lang=lang).items():
        st.markdown(f"**{policy_name(name, lang)}.** {sentence}")

    st.plotly_chart(terminal_figure(res, lang=lang), width="stretch")

    st.subheader(t["when"])
    st.markdown(t["when_md"])

    with st.expander(t["detail"]):
        detail = results_table(res, p, W0, W_ref)
        if lang == "en":
            detail = detail.rename(columns=RESULT_COLS_EN, index=lambda n: policy_name(n, lang))
            detail["Class"] = [klass_name(k, lang) for k in detail["Class"]]
            detail.index.name = "Policy"
        st.dataframe(detail, width="stretch")
