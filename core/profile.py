"""Parte 1: cuestionario y estimación de los parámetros de prospect theory."""
from dataclasses import dataclass, asdict
import math
import numpy as np

LAM_RATIOS = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
LAM_MIN, LAM_MAX = 1.0, 5.0
CURV_MIN, CURV_MAX = 0.2, 1.0

LAMBDA_QUESTIONS = [{"id": f"lam_{L}", "loss": L} for L in (5, 10, 20)]
ALPHA_QUESTIONS = [{"id": f"alpha_{G}", "stake": G} for G in (10, 30)]
BETA_QUESTIONS = [{"id": f"beta_{L}", "stake": L} for L in (10, 30)]

BIAS_QUESTIONS = [
    {"id": "b1", "text": "Tu portafolio cayó 20% en los últimos tres meses. ¿Qué haces?",
     "options": ["Vendo todo y paso a efectivo", "Vendo una parte", "No hago nada", "Aprovecho y compro más"]},
    {"id": "b2", "text": "Si hubieras vendido, ¿cuándo volverías a invertir?",
     "options": ["Cuando el mercado rebote 5% desde el mínimo", "Cuando rebote 15% desde el mínimo",
                 "Cuando recupere todo lo perdido"]},
    {"id": "b3", "text": "Un ETF subió 40% en el último año y tu portafolio solo 5%. ¿Qué haces?",
     "options": ["Muevo buena parte de mi dinero a ese ETF", "Muevo un poco", "Nada, sigo mi plan"]},
    {"id": "b4", "text": "¿Cada cuánto revisas y ajustas tu portafolio?",
     "options": ["Cada mes", "Cada trimestre", "Una vez al año"]},
]
BIAS_QUESTIONS_EN = [   # mismas preguntas y mismo orden de opciones, en inglés
    {"id": "b1", "text": "Your portfolio fell 20% over the last three months. What do you do?",
     "options": ["Sell everything and move to cash", "Sell part of it", "Do nothing", "Take the chance to buy more"]},
    {"id": "b2", "text": "If you had sold, when would you invest again?",
     "options": ["When the market rebounds 5% from the bottom", "When it rebounds 15% from the bottom",
                 "When it recovers everything that was lost"]},
    {"id": "b3", "text": "One ETF rose 40% last year and your portfolio only 5%. What do you do?",
     "options": ["Move a large part of my money into that ETF", "Move a little", "Nothing, I stick to my plan"]},
    {"id": "b4", "text": "How often do you review and adjust your portfolio?",
     "options": ["Every month", "Every quarter", "Once a year"]},
]


def bias_questions(lang="es"):
    return BIAS_QUESTIONS_EN if lang == "en" else BIAS_QUESTIONS


B1_MAP = [(True, 0.10, 1.0), (True, 0.20, 0.5), (False, None, None), (False, None, None)]  # (pánico, d, φ)
B2_MAP = [0.05, 0.15, 0.25]   # r
B3_MAP = [0.50, 0.25, 0.0]    # κ
B4_MAP = [1, 3, 12]           # f (meses)

DEFAULT_ANSWERS = {
    "lam_5": 2.0, "lam_10": 2.0, "lam_20": 2.5,
    "alpha_10": 4.0, "alpha_30": 12.0, "beta_10": 4.0, "beta_30": 12.0,
    "b1": 2, "b2": 1, "b3": 2, "b4": 1,
}


def lambda_text(L, lang="es"):
    if lang == "en":
        return (f"We flip a coin. Heads, you lose {L}% of your portfolio; tails, you win G%. "
                f"What is the smallest gain G for which you would accept the bet?")
    return (f"Lanzamos una moneda. Si sale cara pierdes el {L}% de tu portafolio; si sale sello ganas G%. "
            f"¿Cuál es la ganancia G más pequeña con la que aceptarías jugar?")


def lambda_options(L, lang="es"):
    """Lista de (etiqueta, razón G/L); None = no aceptaría."""
    no = "I would not accept any of these" if lang == "en" else "No aceptaría con ninguna de estas"
    return [(f"{L * r:g}%", r) for r in LAM_RATIOS] + [(no, None)]


def alpha_text(G, lang="es"):
    if lang == "en":
        return (f"You can keep a bet (50%: you win {G}% of your portfolio; 50%: you win nothing) or take a sure "
                f"gain. What is the smallest sure gain (in %) for which you would give up the bet?")
    return (f"Puedes quedarte con una apuesta (50%: ganas el {G}% de tu portafolio; 50%: no ganas nada) "
            f"o recibir una ganancia segura. ¿Cuál es la ganancia segura mínima (en %) por la que cambiarías la apuesta?")


def beta_text(L, lang="es"):
    if lang == "en":
        return (f"You must choose between a bet (50%: you lose {L}% of your portfolio; 50%: you lose nothing) "
                f"or a sure loss. What is the largest sure loss (in %) you would accept to avoid the bet?")
    return (f"Debes elegir entre una apuesta (50%: pierdes el {L}% de tu portafolio; 50%: no pierdes nada) "
            f"o una pérdida segura. ¿Cuál es la pérdida segura máxima (en %) que aceptarías para evitar la apuesta?")


@dataclass(frozen=True)
class Profile:
    lam: float = 2.25          # aversión a pérdidas λ
    alpha: float = 0.88        # curvatura en ganancias α
    beta: float = 0.88         # curvatura en pérdidas β
    lam_curv: float = float("nan")   # λ corregido por curvatura (solo informativo)
    panic: bool = False        # ¿vende en pánico?
    d: float = 0.20            # caída que dispara la venta
    r: float = 0.15            # rebote desde el mínimo para volver a invertir
    phi: float = 1.0           # fracción que vende
    chase: bool = False        # ¿persigue rendimientos?
    kappa: float = 0.25        # fracción que mueve a los ganadores
    f: int = 3                 # cada cuántos meses persigue
    top_k: int = 3             # número de ganadores

    def as_dict(self):
        return asdict(self)


def curvature_from_ce(ce, stake):
    """α (o β) a partir del equivalente cierto de una lotería 50/50 entre `stake` y 0."""
    ratio = min(max(float(ce) / float(stake), 0.01), 0.99)
    return float(np.clip(math.log(0.5) / math.log(ratio), CURV_MIN, CURV_MAX))


def estimate_profile(answers=None):
    """Respuestas del cuestionario → Profile. Las respuestas que falten toman su valor por defecto."""
    a = {**DEFAULT_ANSWERS, **(answers or {})}
    ratios = [LAM_MAX if a[q["id"]] is None else float(a[q["id"]]) for q in LAMBDA_QUESTIONS]
    lam = float(np.clip(np.median(ratios), LAM_MIN, LAM_MAX))
    alpha = float(np.mean([curvature_from_ce(a[q["id"]], q["stake"]) for q in ALPHA_QUESTIONS]))
    beta = float(np.mean([curvature_from_ce(a[q["id"]], q["stake"]) for q in BETA_QUESTIONS]))
    lam_curv = float(np.median([((r * q["loss"] / 100) ** alpha) / ((q["loss"] / 100) ** beta)
                                for r, q in zip(ratios, LAMBDA_QUESTIONS)]))
    panic, d, phi = B1_MAP[int(a["b1"])]
    kappa = B3_MAP[int(a["b3"])]
    base = Profile()
    return Profile(
        lam=lam, alpha=alpha, beta=beta, lam_curv=lam_curv,
        panic=panic, d=d if panic else base.d, r=B2_MAP[int(a["b2"])], phi=phi if panic else base.phi,
        chase=kappa > 0, kappa=kappa if kappa > 0 else base.kappa, f=B4_MAP[int(a["b4"])],
    )


def describe_profile(p, lang="es"):
    """Frases en lenguaje simple para el cliente."""
    if lang == "en":
        return _describe_profile_en(p)
    level = "baja" if p.lam < 1.5 else ("moderada" if p.lam < 2.5 else "alta")
    out = [f"**Aversión a pérdidas {level} (λ = {p.lam:.2f}).** Una pérdida te pesa {p.lam:.1f} veces "
           f"lo que te alegra una ganancia del mismo tamaño."]
    if p.alpha < 0.95:
        out.append(f"**Con ganancias prefieres asegurar (α = {p.alpha:.2f}).** Cambiarías una apuesta por una "
                   f"ganancia segura menor que su valor esperado.")
    else:
        out.append(f"**Con ganancias eres casi neutral al riesgo (α = {p.alpha:.2f}).**")
    if p.beta < 0.95:
        out.append(f"**Con pérdidas tiendes a arriesgar (β = {p.beta:.2f}).** Prefieres apostar antes que "
                   f"aceptar una pérdida segura.")
    else:
        out.append(f"**Con pérdidas eres casi neutral al riesgo (β = {p.beta:.2f}).**")
    if p.panic:
        out.append(f"**Sesgo detectado: venta por pánico.** Venderías el {p.phi:.0%} de tu portafolio tras una "
                   f"caída de {p.d:.0%} y volverías a invertir cuando el mercado rebote {p.r:.0%}.")
    if p.chase:
        each = "cada mes" if p.f == 1 else f"cada {p.f} meses"
        out.append(f"**Sesgo detectado: persecución de rendimiento.** {each.capitalize()} moverías el "
                   f"{p.kappa:.0%} de tu dinero hacia los activos que más subieron en el último año.")
    if not (p.panic or p.chase):
        out.append("**No detectamos sesgos de comportamiento** en tus respuestas.")
    return out


def _describe_profile_en(p):
    level = "low" if p.lam < 1.5 else ("moderate" if p.lam < 2.5 else "high")
    out = [f"**{level.capitalize()} loss aversion (λ = {p.lam:.2f}).** A loss weighs on you {p.lam:.1f} times "
           f"as much as a gain of the same size pleases you."]
    if p.alpha < 0.95:
        out.append(f"**With gains you prefer to lock them in (α = {p.alpha:.2f}).** You would trade a bet for a "
                   f"sure gain smaller than its expected value.")
    else:
        out.append(f"**With gains you are almost risk-neutral (α = {p.alpha:.2f}).**")
    if p.beta < 0.95:
        out.append(f"**With losses you tend to take risks (β = {p.beta:.2f}).** You would rather gamble than "
                   f"accept a sure loss.")
    else:
        out.append(f"**With losses you are almost risk-neutral (β = {p.beta:.2f}).**")
    if p.panic:
        out.append(f"**Bias detected: panic selling.** You would sell {p.phi:.0%} of your portfolio after a "
                   f"{p.d:.0%} drop and invest again once the market rebounds {p.r:.0%}.")
    if p.chase:
        each = "every month" if p.f == 1 else f"every {p.f} months"
        out.append(f"**Bias detected: performance chasing.** {each.capitalize()} you would move {p.kappa:.0%} "
                   f"of your money into the assets that rose the most over the last year.")
    if not (p.panic or p.chase):
        out.append("**We did not detect behavioral biases** in your answers.")
    return out


def pt_value(x, alpha, beta, lam):
    """Función de valor de prospect theory: x^α si x ≥ 0; −λ(−x)^β si x < 0."""
    x = np.asarray(x, dtype=float)
    ax = np.abs(x)
    return np.where(x >= 0, ax ** alpha, -lam * ax ** beta)
