# Spec — Proyecto A: Dashboard de portafolio conductual

> Estado: `ready-for-agent`. Entregable final: **un solo `.ipynb`** que también genera la app de Streamlit.
> Las decisiones marcadas **[R2]** no se discutieron en la entrevista: son mis recomendaciones por defecto y conviene revisarlas.

---

## Problem Statement

Una firma de asesoría necesita mostrarle a un inversionista individual tres cosas que hoy no puede cuantificar de forma clara:

1. **Quién es como inversionista**: cuánto le duelen las pérdidas frente a las ganancias (λ), cómo valora ganancias y pérdidas de distinto tamaño (α, β) y qué sesgos tiene (vender en pánico, perseguir rendimientos).
2. **Qué portafolio le conviene**, de forma coherente con ese perfil y con restricciones prácticas: pocos activos, posiciones mínimas, diversificación por clase de activo.
3. **Cuánto le cuesta su propio comportamiento** a 10 años, comparado con seguir una regla disciplinada, expresado en dinero y en lenguaje simple, con la incertidumbre de los resultados visible y no solo un promedio.

Además, el trabajo tiene que cumplir un encargo académico: modelo de Powell con sus cinco elementos, al menos dos políticas de clases distintas más un baseline, evaluación con números aleatorios comunes (≥500 escenarios, semillas separadas para ajuste y evaluación, media, dispersión e intervalo de confianza), una recomendación con sus condiciones, y un dashboard en Streamlit. Plazo: una semana.

## Solution

Un notebook único y reproducible que:

- descarga 24 ETFs con yfinance desde 2008-01 hasta 2026-10 y los convierte a retornos mensuales;
- implementa un **cuestionario de 11 preguntas** que estima λ, α y β de prospect theory y marca sesgos;
- construye el portafolio con un **MILP media-CVaR en Gurobi** cuyo límite de CVaR depende de λ;
- simula 10 años mes a mes con **bootstrap circular por bloques de 3 a 6 meses**, y compara un baseline, dos políticas que optimizan (PFA de bandas, CFA que vuelve a resolver el MILP cada año) y dos políticas conductuales (venta por pánico, persecución de rendimiento) sobre los mismos escenarios;
- ajusta los parámetros con una semilla y evalúa con otra en 1000 escenarios;
- escribe una recomendación;
- genera el código de la app (`core` y `app`) con celdas `%%writefile`, para que el cliente llene el cuestionario y vea su perfil, su portafolio, el gráfico de abanico de su riqueza y el costo en dinero de sus sesgos.

## User Stories

**Cliente (inversionista individual)**

1. Como cliente, quiero responder un cuestionario corto (unas 11 preguntas) en lenguaje simple, para obtener mi perfil sin conocimientos técnicos.
2. Como cliente, quiero que las loterías estén en % de mi portafolio, para imaginar el impacto real sobre mis ahorros.
3. Como cliente, quiero ver mi aversión a pérdidas (λ) traducida a una frase ("una pérdida te duele 2,3 veces más que una ganancia del mismo tamaño"), para entender el número.
4. Como cliente, quiero ver mis curvaturas α y β explicadas ("prefieres asegurar ganancias" / "arriesgas para evitar pérdidas"), para reconocerme en el perfil.
5. Como cliente, quiero ver qué sesgos se detectaron y con qué intensidad, para saber qué conductas me afectan.
6. Como cliente, quiero ver mi portafolio recomendado como tabla y gráfico (activo, clase, peso), para saber exactamente qué comprar.
7. Como cliente, quiero ver la pérdida típica de mi portafolio en un mal mes (CVaR 95%), para saber qué esperar en una crisis.
8. Como cliente, quiero ver un gráfico de abanico con mi riqueza simulada a 10 años (percentiles 5–25–50–75–95), para entender el rango de resultados posibles.
9. Como cliente, quiero ver cuánto dinero me cuesta, en la mediana, vender en pánico frente a rebalancear con disciplina, para dimensionar el costo de esa conducta.
10. Como cliente, quiero ver el mismo costo para la persecución de rendimiento, para comparar mis sesgos entre sí.
11. Como cliente, quiero ver el costo combinado de "yo tal como soy" frente a "yo disciplinado", para tener un solo número que resuma el efecto de mi comportamiento.
12. Como cliente, quiero leer la comparación de políticas en frases simples ("en 9 de cada 10 escenarios terminas con más de…"), para no tener que interpretar estadísticas.
13. Como cliente, quiero ver una recomendación clara de qué regla seguir, para saber qué hacer cada mes.
14. Como cliente, quiero ver bajo qué condiciones cambiaría la recomendación, para saber cuándo volver a consultar.
15. Como cliente, quiero cambiar mi riqueza inicial, para ver resultados en mi escala.
16. Como cliente, quiero fijar opcionalmente una meta de crecimiento anual como punto de referencia, para medir el éxito contra mi objetivo y no solo contra no perder.
17. Como cliente, quiero corregir mis respuestas y ver los resultados recalculados, para explorar "qué pasaría si fuera más tolerante al riesgo".

**Asesor (usuario de la firma)**

18. Como asesor, quiero ajustar K (número máximo de activos), la posición mínima l, la máxima u y el tope por clase de activo, para adaptar el portafolio a las reglas de la firma.
19. Como asesor, quiero sobrescribir λ, α y β a mano, para probar sensibilidad sin repetir el cuestionario.
20. Como asesor, quiero activar o desactivar cada sesgo y ajustar sus parámetros (d, r, φ, κ, frecuencia), para mostrarle al cliente escenarios hipotéticos.
21. Como asesor, quiero una tabla con media, desviación estándar, percentiles 5/95 e intervalo de confianza del 95% del valor de prospect theory y de la riqueza final por política, para respaldar la recomendación.
22. Como asesor, quiero ver la rotación y los costos de transacción por política, para explicar por qué una regla que opera más no siempre gana.
23. Como asesor, quiero ver la caída máxima por política, para hablar de riesgo vivido y no solo de riqueza final.
24. Como asesor, quiero que la app cargue los datos y parámetros ajustados guardados por el notebook, para no depender de yfinance en la reunión.
25. Como asesor, quiero que la CFA (más lenta) se calcule al pulsar un botón y quede en caché, para que la app responda rápido por defecto.

**Evaluador del curso / analista**

26. Como evaluador, quiero ver el modelo de Powell escrito con estado, decisión, información exógena, transición y objetivo, con unidades y con lo que se conoce en cada decisión, para verificar el planteamiento.
27. Como evaluador, quiero que cada política declare su clase (PFA/CFA/baseline/conductual) y sus parámetros ajustables, para verificar el requisito 2.
28. Como evaluador, quiero ver que todas las políticas usan la misma matriz de escenarios, para verificar los números aleatorios comunes.
29. Como evaluador, quiero ver semillas distintas para ajuste (300 escenarios) y evaluación (1000 escenarios), para verificar que no hay sobreajuste.
30. Como evaluador, quiero ver las curvas de ajuste (métrica frente a b; métrica frente a θ y ventana), para entender cómo se eligieron los parámetros.
31. Como evaluador, quiero ver intervalos de confianza normales y por bootstrap de la media, para juzgar si las diferencias son significativas.
32. Como evaluador, quiero ver diferencias pareadas entre políticas (misma ruta, política A − política B) con su intervalo, para que la comparación aproveche los números aleatorios comunes.
33. Como evaluador, quiero que el notebook corra de principio a fin en Colab con la licencia restringida de gurobipy, para reproducirlo.
34. Como evaluador, quiero celdas de verificación (asserts) que validen las propiedades clave, para confiar en el código.
35. Como evaluador, quiero ver la justificación de cada método (por qué MILP media-CVaR, por qué bootstrap por bloques, por qué estas clases de política), para cumplir "justificar la elección".
36. Como analista, quiero un análisis de sensibilidad de la recomendación frente a λ, costos de transacción y punto de referencia, para fundamentar las condiciones de cambio.

## Implementation Decisions

### Entorno y entregable
- Se corre en **Google Colab** con `gurobipy` instalado por pip y su licencia restringida (≤2000 variables y ≤2000 restricciones). Con una licencia académica corre igual.
- **Un solo notebook** con secciones en este orden: Datos → Modelo de Powell → Cuestionario → MILP → Escenarios → Políticas → Ajuste → Evaluación → Recomendación → Generación de la app.
- Texto en **español** y código en **inglés**.
- La lógica vive en un módulo `core` que el notebook escribe a disco con `%%writefile` y luego importa. La app de Streamlit importa el mismo módulo, así que el notebook y la app no pueden divergir.
- El notebook guarda en disco los retornos mensuales, el mapa de tickers a clase de activo y un JSON con los parámetros ajustados. La app los carga.

### Datos
- Universo de 24 ETFs en 5 clases de activo, que funcionan como "sectores":
  - Acciones de EE.UU. por sector: XLK, XLF, XLV, XLE, XLI, XLY, XLP, XLU, XLB
  - Acciones internacionales: EFA, EEM, VGK, EWJ
  - Renta fija: TLT, IEF, SHY, LQD, HYG, TIP
  - Activos reales: VNQ, GLD, SLV, DBC
  - Efectivo: BIL
- Precios diarios ajustados desde 2008-01-01 hasta el último mes completo (2026-10). Retorno mensual = último precio del mes / último precio del mes anterior − 1. Unos 226 meses.
- BIL puede entrar en el MILP y es el destino de la venta por pánico.

### Perfil (cuestionario)
- Todas las loterías se expresan en **% del portafolio**, para que α, β y λ estén en las mismas unidades que x en la simulación.
- **λ (3 preguntas)**: lotería 50/50 "perder L% / ganar G%" con L ∈ {5, 10, 20}. El cliente elige de una lista la menor G con la que aceptaría (G/L ∈ {1, 1.5, 2, 2.5, 3, 4, 5, "nunca"}). λ = mediana de G/L, acotada a [1, 5]; "nunca" cuenta como 5. Se reporta aparte el λ corregido por curvatura, G^α / L^β.
- **α (2 preguntas)**: equivalente cierto de 50% ganar G / 50% nada, con G ∈ {10%, 30%}. α = ln(0.5) / ln(CE/G), promedio de las dos, acotado a [0.2, 1].
- **β (2 preguntas)**: lo mismo con pérdidas de 10% y 30%. Equivalente cierto en valor absoluto.
- **Sin ponderación de probabilidades**: solo se usa v(x).
- **Sesgos (4 preguntas) [R2]**:
  - **B1 – "Tu portafolio cayó 20% en tres meses. ¿Qué haces?"**
    - Vendo todo y paso a efectivo → pánico, d = 10%, φ = 1
    - Vendo una parte → pánico, d = 20%, φ = 0.5
    - No hago nada / compro más → sin pánico
  - **B2 – "Si vendiste, ¿cuándo volverías a invertir?"**
    - Cuando el mercado rebote 5% desde el mínimo → r = 5%
    - Cuando rebote 15% → r = 15%
    - Cuando recupere todo lo perdido → r = 25%

    Solo se usa si B1 indica pánico.
  - **B3 – "Un ETF subió 40% en el último año y el tuyo 5%. ¿Qué haces?"**
    - Muevo buena parte a ese ETF → κ = 0.5
    - Muevo un poco → κ = 0.25
    - Nada → κ = 0, sin persecución
  - **B4 – "¿Cada cuánto revisas y ajustas tu portafolio?"** Mensual / trimestral / anual. Fija la frecuencia f de la persecución de rendimiento.
- Salida: un objeto Profile con λ, α, β, el λ corregido y los parámetros de sesgo (flags, d, r, φ, κ, f, top-k = 3).

### Portafolio (MILP media-CVaR en Gurobi)
- Variables:
  - w_i ≥ 0: peso del activo i, en fracción.
  - z_i ∈ {0,1}: indica si el activo i entra al portafolio.
  - ζ: el VaR.
  - u_s ≥ 0: exceso de pérdida en el escenario s.
- Escenarios: los meses históricos de la ventana de estimación.
- Objetivo: **maximizar el retorno mensual esperado** μᵀw.
- Restricciones:
  - Σw = 1, sin posiciones cortas.
  - Σz ≤ K.
  - l·z_i ≤ w_i ≤ u·z_i.
  - Peso por clase de activo ≤ tope por clase.
  - Linealización de Rockafellar–Uryasev: CVaR₉₅ = ζ + (1 / (0.05·S)) Σu_s ≤ c(λ), con u_s ≥ −r_sᵀw − ζ.
- **Vínculo con λ [R2]**: c(λ) = θ · [c_max − (c_max − c_min)·(λ − 1)/4], con c_max = 10% y c_min = 2% (CVaR mensual), interpolado linealmente sobre λ ∈ [1, 5]. θ = 1 en la Parte 2; la CFA lo ajusta.
- **Valores por defecto [R2]**: K = 8, l = 5%, u = 35%, tope por clase = 50%. Todos se pueden mover en el dashboard.
- Si el problema resulta infactible, cae a "minimizar CVaR" con las mismas restricciones y avisa.
- Interfaz: recibe el perfil, la matriz de retornos de la ventana y las restricciones. Devuelve los pesos, los activos elegidos, la media y el CVaR del portafolio, y el estado del solver.
- El modelo de Gurobi se construye una sola vez y se reutiliza actualizando coeficientes, porque la CFA lo resuelve miles de veces.

### Escenarios
- **Bootstrap circular por bloques**: la longitud de cada bloque se sortea uniformemente en {3, 4, 5, 6} meses. Se toman filas completas, todos los activos del mismo mes juntos, para conservar las correlaciones entre activos.
- Se genera un tensor (escenarios × 120 meses × 24 activos) por semilla:
  - semilla de ajuste: 300 escenarios;
  - semilla de evaluación: 1000 escenarios.
- **Números aleatorios comunes**: todas las políticas reciben el mismo tensor.

### Modelo de Powell (simulador)
- **Tiempo**: t = 0, …, 120 meses. La decisión x_t se toma al inicio del mes t, conociendo todo lo ocurrido hasta el cierre de t−1. Durante el mes llega R_{t+1}.
- **Estado S_t**:
  - W_t: riqueza en USD.
  - w_t: pesos después de la deriva del mes, en fracción.
  - P_t: máximo de riqueza hasta la fecha, en USD.
  - H_t: retornos de los últimos 12 meses por activo, que combinan historia previa y meses simulados.
  - Para la política de pánico: m_t ∈ {invertido, en efectivo} y el mínimo M_t, desde la salida, del índice de mercado I_t (portafolio w*, I_0 = 1).
  - Para la CFA: pesos objetivo vigentes y meses desde el último re-solve.
- **Decisión x_t**: los montos que se compran o venden de cada activo (USD). De forma equivalente, los pesos después de operar, w⁺_t.
- **Información exógena** W_{t+1}: el vector R_{t+1} de retornos del mes, sorteado por el bootstrap.
- **Transición**:
  - Costo: W⁺_t = W_t − 0.001 · Σ|x_t|, es decir 10 pb sobre el valor operado.
  - Riqueza: W_{t+1} = W⁺_t · (1 + w⁺_tᵀR_{t+1}).
  - Pesos: w_{t+1} = w⁺_t ⊙ (1 + R_{t+1}) / (1 + w⁺_tᵀR_{t+1}).
  - Además se actualizan P, H, m y M.
- **Objetivo**: maximizar E[v(x)] con x = (W_T − W_ref)/W_0, v(x) = x^α si x ≥ 0 y −λ(−x)^β si x < 0. Por defecto W_ref = W_0; opcionalmente W_ref = W_0·(1+g)^10. W_0 por defecto = USD 100.000. Sin aportes, en términos nominales.
- **Métricas reportadas**:
  - Métrica principal: valor PT.
  - Riqueza final: media, P5, P25, P50, P75, P95.
  - Caída máxima.
  - Rotación y costos pagados.

### Políticas
Todas cumplen la misma interfaz: reciben el estado y los parámetros y devuelven los pesos después de operar.

| Política | Clase | Regla | Parámetros ajustables |
|---|---|---|---|
| Comprar y mantener | Baseline | Comprar el portafolio de la Parte 2 en t = 0 y no operar más | — |
| Bandas | PFA | Si algún \|w_i − w*_i\| > b, rebalancear todo a w* | b ∈ {2, 3, 5, 7.5, 10, 15, 20}% **[R2]** |
| Re-solve anual | CFA | Cada 12 meses, resolver de nuevo el MILP con c(λ)·θ sobre una ventana de los últimos N meses (historia previa + simulados) y llevar el portafolio a la solución | θ ∈ {0.75, 1, 1.25}, N ∈ {36, 60, 120} **[R2]** |
| Venta por pánico | Conductual | Encima de la política disciplinada: si la caída desde P llega a d, vender una fracción φ a BIL; volver a invertir cuando el índice de mercado I (portafolio w*) rebote r desde su mínimo M | d, r, φ (del cuestionario) |
| Persecución de rendimiento | Conductual | Encima de la política disciplinada: cada f meses, mover una fracción κ hacia los 3 activos con mejor retorno a 12 meses | κ, f, top-k (del cuestionario) |
| Cliente como es | Conductual combinada | Aplica los sesgos que el cuestionario detectó | — |

- **Base de los sesgos [R2]**: las políticas conductuales se aplican encima de la política disciplinada recomendada (PFA con el b* ajustado).
- **Costo de un sesgo** = diferencia en la mediana de riqueza final (y en el valor PT) frente a la PFA sola, en los mismos escenarios.
- Si el cliente no tiene un sesgo, la app igual muestra su costo con parámetros típicos, como escenario hipotético.

### Ajuste y evaluación
- **Ajuste**: búsqueda en cuadrícula con la semilla de ajuste (300 escenarios). Se maximiza el valor PT medio para un perfil de referencia (λ = 2.25, α = β = 0.88). El JSON guarda b*, θ* y N*.
- **Evaluación final**: semilla de evaluación, 1000 escenarios, todas las políticas. Para cada métrica se reporta:
  - media, desviación estándar, P5 y P95;
  - IC del 95% de la media, normal y por bootstrap;
  - diferencias pareadas frente a la PFA, con su IC.
- **Sensibilidad [R2]**: la recomendación se repite con λ ∈ {1, 2.25, 4}, costos ∈ {10, 50} pb y referencia ∈ {W_0, meta 4% anual}.
- **Regla de recomendación**: la política con mayor valor PT medio. Si el IC de la diferencia pareada contiene 0, se recomienda la más simple (PFA antes que CFA). Las condiciones de cambio salen de la sensibilidad.

### App de Streamlit [R2]
- **Barra lateral**: riqueza inicial, meta opcional, K, l, u, tope por clase, y sobrescritura manual de λ, α y β.
- **Pestaña 1 – Cuestionario**: muestra el perfil resultante con frases explicativas.
- **Pestaña 2 – Mi portafolio**: tabla, gráfico de dona por clase de activo y CVaR explicado.
- **Pestaña 3 – Mi futuro**: gráfico de abanico de la política recomendada y del "cliente como es".
- **Pestaña 4 – Comparar reglas**: tabla en lenguaje simple con el costo en USD de cada sesgo y la recomendación.
- **Cálculo en vivo**: MILP, baseline, PFA y conductuales, con 500 escenarios vectorizados en numpy.
- **CFA**: se calcula al pulsar un botón y queda en caché.
- Los parámetros ajustados vienen del JSON del notebook.
- Los gráficos se hacen con Plotly.

## Testing Decisions

- **Qué es un buen test**: verifica comportamiento observable a través de la interfaz pública del módulo `core`, no detalles internos. Usa casos con respuesta conocida (retornos cero, perfiles neutrales al riesgo, parámetros extremos) y propiedades que siempre deben cumplirse. Va en celdas de assert del notebook, que fallan de forma visible.
- **Costura propuesta (una sola)**: la interfaz pública de `core`, con tres puntos de entrada:
  1. respuestas → Profile;
  2. (Profile, retornos, restricciones) → Portfolio;
  3. (políticas, tensor de escenarios, Profile) → resultados por política.

  La app y el notebook consumen exactamente esa interfaz.
- **Módulos que se prueban y casos**:
  - **Perfil**:
    - CE = 50% del premio da α ≈ 1.
    - Aceptar con G/L = 1 da λ = 1.
    - Las cotas se respetan.
    - Cada opción de sesgo produce los parámetros de la tabla.
  - **MILP**:
    - Σw = 1, w ≥ 0, Σz ≤ K y l ≤ w ≤ u cuando z = 1.
    - Ninguna clase supera su tope.
    - El CVaR ex post sobre la ventana es ≤ c(λ).
    - Al subir λ, el CVaR no aumenta y la media no aumenta.
  - **Escenarios**:
    - Misma semilla, mismo tensor; semillas distintas, tensores distintos.
    - Cada fila del tensor es una fila histórica completa.
    - Las longitudes de bloque están en {3, …, 6}.
  - **Simulador y políticas**:
    - Con retornos cero, comprar y mantener conserva W_0 menos el costo inicial.
    - La PFA con b muy grande equivale a comprar y mantener.
    - La PFA con b = 0 paga 10 pb × rotación.
    - El pánico con d = 100% equivale a la PFA.
    - La persecución con κ = 0 equivale a la PFA.
    - La CFA con θ = 1 y ventana completa reproduce en t = 0 los pesos de la Parte 2.
    - Todas las políticas consumen el mismo tensor.
  - **Evaluación**: el IC contiene la media; la diferencia pareada de una política consigo misma es 0.
- **Prior art**: no hay código previo (proyecto nuevo); los tests siguen el patrón de propiedades descrito arriba.

## Out of Scope

- Ponderación de probabilidades (π) de prospect theory acumulativa.
- Impuestos, aportes o retiros periódicos, inflación, apalancamiento, posiciones cortas.
- Políticas VFA y DLA.
- Datos en vivo dentro de la app: la app usa los datos guardados por el notebook.
- Despliegue público en Streamlit Cloud: solo se documenta cómo lanzarla.
- Validación empírica del cuestionario con personas reales.
- Decisiones dentro del mes; el paso de tiempo es mensual.

## Further Notes

- **Sesgo de anticipación en la CFA**: el bootstrap y el MILP de la Parte 2 usan la misma historia. Se documenta como limitación, y la ventana móvil de la CFA incorpora los meses simulados.
- **Tiempo de cómputo**: la CFA en ajuste son 9 combinaciones × 300 escenarios × 10 re-solves, unas 27.000 resoluciones pequeñas. Se reutiliza un solo modelo de Gurobi, con salida silenciosa. Si tarda demasiado en Colab, se baja el ajuste de la CFA a 150 escenarios y se documenta.
- **Escala de la potencia**: con α ≠ β, la escala de x importa. Por eso se usa x relativo a W_0, tanto en el cuestionario como en el objetivo.
- **Plazo**: una semana. Orden de construcción sugerido: datos y escenarios → simulador y baseline → MILP → PFA y conductuales → CFA → evaluación → app.
