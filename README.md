# Dashboard de portafolio conductual

[![Abrir el dashboard](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dashboard-portafolio-conductual.streamlit.app)

Una herramienta para que un asesor financiero haga tres cosas con un cliente:

1. **Perfilarlo** con un cuestionario de 11 preguntas, que estima sus parámetros de prospect theory (aversión a pérdidas λ y curvaturas α, β) y detecta dos sesgos: venta por pánico y persecución de rendimiento.
2. **Construirle un portafolio** con un MILP media-CVaR resuelto con Gurobi, cuyo límite de riesgo de cola depende de λ.
3. **Mostrarle cuánto le cuesta su propio comportamiento** a 10 años, simulando mes a mes con el marco de Powell y comparando reglas disciplinadas con reglas que imitan sus sesgos.

👉 **[Abrir el dashboard](https://dashboard-portafolio-conductual.streamlit.app)**. Funciona en el navegador, también desde el celular, sin instalar nada.

👉 **[Ver el notebook completo con resultados](portafolio_conductual.ipynb)**. GitHub lo muestra con todas sus tablas y gráficos.

---

## Qué hay en este repositorio

| Ruta | Contenido |
|---|---|
| [`portafolio_conductual.ipynb`](portafolio_conductual.ipynb) | El informe completo: datos, modelo de Powell, cuestionario, MILP, simulador, políticas, ajuste, evaluación, sensibilidad y recomendación. Incluye las pruebas (`assert`). |
| [`app.py`](app.py) | El dashboard de Streamlit. |
| [`core/`](core) | La lógica compartida por el notebook y la app: `profile` (cuestionario), `portfolio` (MILP), `scenarios` (bootstrap), `policies`, `simulator`, `evaluation` y `plots`. |
| [`data/`](data) | Retornos mensuales de los 24 ETFs (2008-01 a 2026-10) y parámetros ajustados. |
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

Riqueza inicial de US$ 100.000, 10 años, 1000 escenarios de evaluación:

| Política | Valor PT medio [IC95%] | Riqueza final P5 | Mediana | P95 | Caída máx. mediana |
|---|---|---|---|---|---|
| Comprar y mantener | 2.286 [2.202, 2.371] | US$ 151.370 | US$ 326.297 | US$ 703.183 | 20.8% |
| Rebalanceo por bandas (b* = 50%) | 2.287 [2.202, 2.371] | US$ 151.370 | US$ 326.297 | US$ 703.183 | 20.8% |
| Re-optimización anual (θ* = 1.25, N* = 120) | 1.909 [1.813, 2.005] | US$ 112.667 | US$ 269.775 | US$ 701.072 | 29.6% |
| Venta por pánico | 1.719 [1.619, 1.819] | US$ 88.853 | US$ 246.408 | US$ 692.301 | 20.4% |
| Persecución de rendimiento | 1.938 [1.866, 2.010] | US$ 141.501 | US$ 289.580 | US$ 601.937 | 19.8% |
| Tú tal como eres (pánico + persecución) | 1.513 [1.427, 1.599] | US$ 88.045 | US$ 234.374 | US$ 596.097 | 19.8% |

**Recomendación: comprar y mantener el portafolio del MILP.**
- **No se distingue de la regla de bandas.** El IC95% de la diferencia pareada de valor PT, [−0.0009, 0.0003], incluye 0, y comprar y mantener es más simple. El ancho de banda óptimo quedó en el máximo de la cuadrícula: con estos datos, rebalancear no agrega valor, porque cortar a los ganadores (tecnología y oro) para volver a los pesos objetivo resta retorno.
- **Re-optimizar cada año es significativamente peor.** Rota mucho el portafolio y persigue la ventana reciente.
- **El comportamiento pesa más que la regla.** Con sus dos sesgos, el cliente de referencia pierde **US$ 91.923 en la mediana** frente a la disciplina (IC95% del costo medio: US$ 83.944 a 96.493) y termina peor en el 88% de los escenarios.

**Cuándo cambiaría:**
- Con λ = 1, λ = 4, costos de 50 pb o una meta de 4% anual, la recomendación no cambió en el análisis de sensibilidad.
- Cambiaría si el cliente no puede seguir la regla en las caídas: ahí lo prioritario es la disciplina, no la regla.
- Cambiaría si el régimen de mercado difiere de 2008–2026: hay que volver a ajustar con datos nuevos.

## Cómo usar el dashboard

1. **Cuestionario:** responde las 11 preguntas y pulsa *Calcular mi perfil*.
2. **Mi portafolio:** qué comprar hoy y cuánto, por clase de activo, y la pérdida típica en meses malos.
3. **Mi futuro:** gráfico de abanico de 500 futuros simulados, con disciplina y "tal como eres".
4. **Comparar reglas:** la recomendación, el costo en dinero de cada sesgo y la comparación en frases simples.

En la barra lateral se cambian la riqueza inicial y la meta. El asesor puede ajustar el máximo de activos, las posiciones mínima y máxima, el tope por clase, λ, α, β y los sesgos.

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

Ejecutar el notebook completo tarda unos 15 minutos. Vuelve a descargar los datos con yfinance y regenera `core/`, `app.py` y `data/`. Gurobi funciona con la licencia restringida que viene con `pip install gurobipy`: el modelo más grande tiene unas 275 variables, dentro del límite.

## Limitaciones

- El bootstrap y el MILP usan la misma historia (2008–2026), así que los resultados reflejan ese periodo, en el que la tecnología y el oro fueron especialmente buenos.
- El cuestionario no está validado con personas reales.
- No se modelan impuestos, aportes, retiros ni inflación, ni la ponderación de probabilidades de prospect theory acumulativa.
- Es una herramienta educativa, no una recomendación de inversión.
