# Dashboard de portafolio conductual

🌐 **Español** · [English](README.en.md)

[![Abrir el dashboard](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dashboard-portafolio-conductual.streamlit.app)

Una herramienta para que un asesor financiero haga tres cosas con un cliente:

1. **Perfilarlo** con un cuestionario de 11 preguntas, que estima sus parámetros de prospect theory (aversión a pérdidas λ y curvaturas α, β) y detecta dos sesgos: venta por pánico y persecución de rendimiento.
2. **Construirle un portafolio** con un MILP media-CVaR resuelto con Gurobi, cuyo límite de riesgo de cola depende de λ.
3. **Mostrarle cuánto le cuesta su propio comportamiento** a 10 años, simulando mes a mes con el marco de Powell y comparando reglas disciplinadas con reglas que imitan sus sesgos.

👉 **[Abrir el dashboard](https://dashboard-portafolio-conductual.streamlit.app)**. Funciona en el navegador, también desde el celular, sin instalar nada. El selector de la barra lateral cambia entre español e inglés.

👉 **[Ver el notebook completo con resultados](portafolio_conductual.ipynb)**. GitHub lo muestra con todas sus tablas y gráficos. Cada celda de texto está en español y luego en inglés.

👉 **[Conceptos explicados de forma sencilla (español e inglés)](docs/GUIDE_ES_EN.md)**: PT, λ, α, β, equivalente cierto, bandas y b\*, CVaR frente a media-varianza, PFA/CFA y las reglas del asesor.

---

## Qué hay en este repositorio

| Ruta | Contenido |
|---|---|
| [`portafolio_conductual.ipynb`](portafolio_conductual.ipynb) | El informe completo: datos, modelo de Powell, cuestionario, MILP, simulador, políticas, ajuste, evaluación, sensibilidad y recomendación. Incluye las pruebas (`assert`). |
| [`app.py`](app.py) | El dashboard de Streamlit (en español e inglés). |
| [`core/`](core) | La lógica compartida por el notebook y la app: `profile` (cuestionario), `portfolio` (MILP), `scenarios` (bootstrap), `policies`, `simulator`, `evaluation`, `plots` e `i18n` (nombres en inglés). |
| [`data/`](data) | Retornos mensuales de los 24 ETFs (2008-01 a 2026-10) y parámetros ajustados. |
| [`docs/GUIDE_ES_EN.md`](docs/GUIDE_ES_EN.md) | Guía bilingüe de los conceptos y resultados. |
| [`docs/SPEC.md`](docs/SPEC.md) | Especificación: historias de usuario y decisiones de diseño. |
| [`docs/tickets/`](docs/tickets) | El plan de trabajo en 9 tickets. |

El notebook genera `core/` y `app.py` con celdas `%%writefile`. Así el informe y la app usan exactamente el mismo código.

## El problema, en el marco de Powell

- **Estado** $S_t$: riqueza, pesos actuales, máximo de riqueza (para medir caídas), retornos de los últimos 12 meses y la memoria propia de cada política.
- **Decisión** $x_t$: los montos que se compran o venden cada mes, sin posiciones cortas.
- **Información exógena**: los retornos del mes, sorteados con bootstrap circular por bloques de 3 a 6 meses sobre la historia real.
- **Transición**: la riqueza evoluciona con los retornos y paga un costo de 10 pb sobre el valor operado.
- **Objetivo**: maximizar $\mathbb{E}[v((W_T - W_{ref})/W_0)]$, con $v$ la función de valor de prospect theory.

Las ecuaciones completas, las unidades y qué se conoce en cada decisión están en la sección 2 del notebook.

## Políticas comparadas

| Política | Clase | Parámetros ajustables |
|---|---|---|
| Comprar y mantener | Baseline | — |
| Rebalanceo por bandas | PFA | ancho de banda $b$ |
| Re-optimización anual (vuelve a resolver el MILP cada 12 meses) | CFA | factor de riesgo $\theta$, ventana $N$ |
| Venta por pánico | Conductual | $d, r, \varphi$ (del cuestionario) |
| Persecución de rendimiento | Conductual | $\kappa, f$ (del cuestionario) |
| Tú tal como eres (los sesgos detectados) | Conductual | — |

El ajuste usa 300 escenarios con la semilla 2026 (150 para la CFA). La evaluación final usa **1000 escenarios con otra semilla (7777)**. Todas las políticas se simulan sobre los mismos escenarios (números aleatorios comunes).

## Resultados (cliente de referencia: λ = 2.25, α = β = 0.88, con ambos sesgos)

Riqueza inicial de US$ 100.000, 10 años, 1000 escenarios de evaluación. Fuente: sección 8 del notebook, celda `results_table(results, REF, W0)`.

| Política | Valor PT medio [IC95%] | Equivalente cierto | Riqueza final P5 | Mediana | P95 | Caída máx. mediana |
|---|---|---|---|---|---|---|
| Comprar y mantener | 2.286 [2.202, 2.371] | US$ 355.928 | US$ 151.370 | US$ 326.297 | US$ 703.185 | 20.8% |
| Rebalanceo por bandas (b* = 50%) | 2.287 [2.202, 2.371] | US$ 355.966 | US$ 151.370 | US$ 326.297 | US$ 703.185 | 20.8% |
| Re-optimización anual (θ* = 1.25, N* = 120) | 1.909 [1.813, 2.005] | US$ 308.474 | US$ 112.667 | US$ 269.775 | US$ 701.073 | 29.6% |
| Venta por pánico | 2.126 [2.040, 2.213] | US$ 335.678 | US$ 133.340 | US$ 304.734 | US$ 699.368 | 20.9% |
| Persecución de rendimiento | 1.938 [1.866, 2.010] | US$ 312.090 | US$ 141.501 | US$ 289.581 | US$ 601.939 | 19.8% |
| Tú tal como eres (pánico + persecución) | 1.830 [1.755, 1.905] | US$ 298.683 | US$ 127.025 | US$ 272.656 | US$ 599.908 | 19.8% |

**Cómo leerla.** El valor PT es un puntaje de satisfacción, no dólares. El **equivalente cierto** lo pasa a dólares: es el monto seguro que el cliente valora igual que la política con todo su riesgo. Por ejemplo, comprar y mantener le vale a este cliente lo mismo que recibir unos US$ 356.000 seguros en 10 años; "tú tal como eres", unos US$ 299.000.

**Recomendación: comprar y mantener el portafolio del MILP.**
- **No se distingue de la regla de bandas.** El IC95% de la diferencia pareada de valor PT, [−0.0009, 0.0003], incluye 0, y comprar y mantener es más simple. El ancho de banda óptimo quedó en el máximo de la cuadrícula: con estos datos, rebalancear no agrega valor. Al no rebalancear crece el peso del activo de mayor retorno (XLK pasa de 35% a 50% en la mediana; el oro baja de 35% a 24%), y la función objetivo casi no castiga el riesgo extra, porque solo el 0.4% de los futuros termina en pérdida.
- **Re-optimizar cada año es significativamente peor en esta evaluación.** Ojo: la evaluación arma el portafolio con la misma historia de la que sortea los futuros, y eso favorece a comprar y mantener (ver la prueba fuera de muestra).
- **El comportamiento cuesta caro.** Con sus dos sesgos, el cliente de referencia pierde **US$ 53.641 en la mediana** (16%) frente a la disciplina (IC95% del costo medio: US$ 53.240 a 61.201) y termina peor en el 86% de los escenarios. Perseguir rendimiento (US$ 36.716) cuesta más que el pánico (US$ 21.563).

**Cuándo cambiaría:**
- Con λ = 1, λ = 4, costos de 50 pb o una meta de 4% anual, la recomendación no cambió en el análisis de sensibilidad.
- Cambiaría si el cliente no puede seguir la regla en las caídas: ahí lo prioritario es la disciplina, no la regla.
- **Cambia si el futuro no se parece a la historia con que se armó el portafolio.** En la prueba fuera de muestra (portafolio con datos anteriores al corte, 300 futuros sorteados de los posteriores), la re-optimización anual le gana a comprar y mantener en los tres cortes:

  | Corte | Comprar y mantener (PT · mediana) | Re-optimización (θ*, N*) | Re-optimización sin ajustar (θ = 1, N = 60) |
  |---|---|---|---|
  | 2014-12 | 1.320 · US$ 221.312 | 1.947 · US$ 285.061 | 1.980 · US$ 294.196 |
  | 2017-12 | 2.114 · US$ 290.625 | 2.669 · US$ 340.271 | 3.018 · US$ 384.065 |
  | 2019-12 | 1.984 · US$ 272.143 | 3.271 · US$ 415.158 | 3.639 · US$ 445.248 |

- **El riesgo sube si nunca se revisa.** Después de 10 años, los pesos de comprar y mantener superan el límite de CVaR del cliente en el 79% de los futuros (mediana 7.85% contra 7.50%). Conviene una revisión anual.

## De dónde sale cada resultado

Cada número de este README y del informe lo imprime una celda del notebook. La tabla dice cuál, qué función de `core` lo calcula y en qué archivo queda guardado.

| Resultado | Notebook: sección y celda | Función | Guardado en |
|---|---|---|---|
| 24 ETFs, 226 retornos mensuales (2008-01 a 2026-10) | §1, celda `from core.data import …` | `download_prices`, `monthly_returns` ([`core/data.py`](core/data.py)) | [`data/monthly_returns.csv`](data/monthly_returns.csv) |
| Retorno, volatilidad y mejor/peor mes por ETF | §1, tabla `summary` | — | — |
| Perfil de las respuestas por defecto (λ = 2, α = β = 0.76) | §3, celda `example = estimate_profile(DEFAULT_ANSWERS)` | `estimate_profile` ([`core/profile.py`](core/profile.py)) | — |
| Cliente de referencia (λ = 2.25, α = β = 0.88, ambos sesgos) | §3, celda `REF = Profile(panic=True, chase=True)` | `Profile` | `data/tuned_params.json` (`reference_profile`) |
| Portafolio de referencia (XLK 35%, GLD 35%, …), retorno de 13.42%, CVaR de 7.50% | §4, celda `port_ref = build_portfolio(REF, rets, CONS)` | `build_portfolio` ([`core/portfolio.py`](core/portfolio.py)) | — |
| λ → límite de CVaR, retorno y número de activos (λ = 1; 2.25; 4; 5) | §4, tabla `frontier` de la celda "Pruebas del MILP" | `build_portfolio`, `cvar_limit` | — |
| b* = 50%, valor PT y costos de cada banda | §7, tabla y gráfico `pfa_tab = tune(…)` | `tune` ([`core/evaluation.py`](core/evaluation.py)) | [`data/tuned_params.json`](data/tuned_params.json) |
| θ* = 1.25, N* = 120 y el mapa de calor de la CFA | §7, tabla y gráfico `cfa_tab = tune(…)` | `tune` | `data/tuned_params.json` |
| Tabla principal: valor PT, IC, equivalente cierto, P5/P50/P95, caída, costos, rotación | §8, celda `table = results_table(results, REF, W0)` | `results_table`, `certainty_equivalent` | — |
| Diferencias pareadas frente a las bandas (IC [−0.0009, 0.0003]) y probabilidad de superarlas | §8, tabla `paired = paired_comparison(…)` | `paired_comparison` | — |
| Costo de cada conducta (US$ 53.641 en la mediana, 86% de los escenarios) | §8, tabla `costs = behavior_costs(…)` | `behavior_costs` | — |
| Gráfico de abanico y cajas de la riqueza final | §8, celda `fan_figure` / `terminal_figure` | [`core/plots.py`](core/plots.py) | — |
| Sensibilidad (λ = 1, λ = 4, 50 pb, meta de 4%) | §9, tabla `sens` | `recommend` | — |
| Diagnóstico: futuros en pérdida (0.4%), deriva de los pesos, CVaR final (79% sobre el límite) | §9, celda `# Diagnóstico` | `pt_scores`, `hist_cvar` | — |
| Prueba fuera de muestra (tres cortes) | §9, tabla `oos` | `evaluate`, `summarize` | — |
| Recomendación final y cuándo cambiaría | §9, celda `rec = recommend(results, REF, W0, W0, CANDIDATES)` | `recommend` | — |

**Los números del dashboard son distintos a propósito.** La app simula **500** escenarios (semilla 7777) para **quien responde el cuestionario** (por defecto λ = 2, α = β = 0.76 y sin sesgos), así que sus montos no coinciden con los del cliente de referencia del informe. Las funciones y la regla de recomendación son las mismas.

## Cómo usar el dashboard

1. **Cuestionario:** responde las 11 preguntas y pulsa *Calcular mi perfil*.
2. **Mi portafolio:** qué comprar hoy y cuánto, por clase de activo, y la pérdida típica en meses malos.
3. **Mi futuro:** gráfico de abanico de 500 futuros simulados, con disciplina y "tal como eres".
4. **Comparar reglas:** la recomendación, el costo en dinero de cada sesgo y la comparación en frases simples.

En la barra lateral se cambian el idioma, la riqueza inicial y la meta. El asesor puede ajustar el máximo de activos, las posiciones mínima y máxima, el tope por clase, λ, α, β y los sesgos.

## Cómo reproducirlo en tu computador

Requiere Python 3.12.

```bash
git clone https://github.com/gemunozortiz-cell/dashboard-portafolio-conductual.git
cd dashboard-portafolio-conductual
python -m venv .venv
# Windows: .venv\Scripts\activate    ·    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py                 # el dashboard
jupyter notebook portafolio_conductual.ipynb   # el informe (requiere: pip install notebook)
```

Ejecutar el notebook completo tarda unos 20 minutos. Vuelve a descargar los datos con yfinance y regenera `core/`, `app.py` y `data/`. Gurobi funciona con la licencia restringida que viene con `pip install gurobipy`: el modelo más grande tiene unas 275 variables, dentro del límite.

## Limitaciones

- El bootstrap y el MILP usan la misma historia (2008–2026), así que los resultados reflejan ese periodo, muy bueno para la tecnología (XLK: 18.6% anual).
- En la prueba fuera de muestra los futuros salen de un periodo corto (82 a 142 meses), y eso favorece a la CFA.
- θ* y N* quedaron en el borde de su cuadrícula.
- El cuestionario no está validado con personas reales.
- No se modelan impuestos, aportes, retiros ni inflación, ni la ponderación de probabilidades de prospect theory acumulativa.
- Es una herramienta educativa, no una recomendación de inversión.
