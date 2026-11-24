# Guía sencilla del proyecto / Simple project guide

Cada concepto aparece primero en **español** 🇪🇸 y luego en **inglés** 🇬🇧.
Each concept appears first in **Spanish** 🇪🇸 and then in **English** 🇬🇧.

Cliente de referencia / Reference client: US$ 100.000 · 10 años / years · λ = 2,25 · α = β = 0,88 · vende en pánico y persigue rendimientos / panic-sells and chases performance.

**Fuentes / Sources.** Cada número viene de una celda del [notebook](../portafolio_conductual.ipynb); las líneas 📍 dicen cuál. La tabla completa está en el README, sección "De dónde sale cada resultado" ([ES](../README.md#de-dónde-sale-cada-resultado) · [EN](../README.en.md#where-each-result-comes-from)).
Every number comes from a cell of the [notebook](../portafolio_conductual.ipynb); the 📍 lines say which one. The full table is in the README, section "Where each result comes from".

---

## 0. Glosario rápido / Quick glossary

| Sigla / Term | Español | English | En una frase / In one sentence |
|---|---|---|---|
| **PT** | Teoría prospectiva (*Prospect Theory*) | Prospect Theory | ES: cómo siente la gente las ganancias y las pérdidas. EN: how people feel gains and losses. |
| **λ** (lambda) | Aversión a pérdidas | Loss aversion | ES: cuántas veces más duele perder que ganar. EN: how many times more a loss hurts than a gain pleases. |
| **α** (alfa) | Curvatura en ganancias | Curvature for gains | ES: qué tanto prefieres asegurar una ganancia. EN: how much you prefer a sure gain. |
| **β** (beta) | Curvatura en pérdidas | Curvature for losses | ES: qué tanto apuestas para evitar una pérdida segura. EN: how much you gamble to avoid a sure loss. |
| **Valor PT** | Satisfacción medida con PT | PT value (satisfaction) | ES: un "puntaje de felicidad", no dólares. EN: a "happiness score", not dollars. |
| **EC / CE** | Equivalente cierto (seguro) | Certainty equivalent | ES: el monto seguro que te deja igual de satisfecho. EN: the sure amount that makes you equally satisfied. |
| **MILP** | Programación lineal entera mixta | Mixed-Integer Linear Programming | ES: optimización con decisiones de sí/no. EN: optimization with yes/no decisions. |
| **CVaR** | Valor en riesgo condicional | Conditional Value at Risk | ES: pérdida promedio en el 5% de los peores meses. EN: average loss in the worst 5% of months. |
| **Media-varianza** | Modelo de Markowitz | Mean-variance (Markowitz) | ES: retorno contra volatilidad. EN: return versus volatility. |
| **PFA** | Aproximación de la función de política | Policy Function Approximation | ES: una regla simple. EN: a simple rule. |
| **CFA** | Aproximación de la función de costo | Cost Function Approximation | ES: un optimizador con perillas ajustables. EN: an optimizer with tunable knobs. |
| **VFA** | Aproximación de la función de valor | Value Function Approximation | ES: estima el valor del futuro. EN: estimates the value of the future. |
| **DLA** | Aproximación con anticipación directa | Direct Lookahead Approximation | ES: simula hacia adelante antes de decidir. EN: simulates ahead before deciding. |
| **b\*** | Ancho de banda óptimo | Optimal band width | ES: el mejor ancho de banda encontrado. EN: the best band width found. |
| **CRN** | Números aleatorios comunes | Common Random Numbers | ES: todas las reglas, mismos futuros. EN: all rules, same futures. |
| **IC 95% / 95% CI** | Intervalo de confianza | Confidence interval | ES: rango probable del valor real. EN: likely range of the true value. |
| **pb / bp** | Puntos básicos (0,01%) | Basis points | ES: 10 pb = 0,1% de costo. EN: 10 bp = 0.1% cost. |

---

## 1. ¿Qué es PT? / What is PT?

🇪🇸 **PT = Prospect Theory (teoría prospectiva)**, de Kahneman y Tversky (Kahneman ganó el Nobel en 2002). Dice tres cosas sencillas:

1. **No miramos cuánto tenemos, sino cuánto ganamos o perdimos** respecto de un punto de referencia. Aquí el punto de referencia son los US$ 100.000 iniciales.
2. **Perder duele más de lo que alegra ganar.** Eso lo mide λ.
3. **Las emociones se "cansan"**: el segundo 10% de ganancia alegra menos que el primero, y el segundo 10% de pérdida duele menos que el primero. Eso lo miden α y β.

La fórmula es la función de valor *v*, aplicada a la ganancia *x* (en fracción de la inversión inicial):

- si ganas (x ≥ 0): v(x) = x^α
- si pierdes (x < 0): v(x) = −λ · (−x)^β

**"Valor PT medio"** = el promedio de v(x) en los 1000 futuros simulados. Es un **puntaje de satisfacción, no dólares**. Más alto es mejor.

🇬🇧 **PT = Prospect Theory**, by Kahneman and Tversky (Kahneman won the Nobel Prize in 2002). It says three simple things:

1. **People care about gains and losses, not total wealth**, measured against a reference point. Here the reference point is the initial US$ 100,000.
2. **Losing hurts more than winning pleases.** λ measures this.
3. **Feelings get "tired"**: the second 10% gain pleases less than the first, and the second 10% loss hurts less than the first. α and β measure this.

The formula is the value function *v*, applied to the gain *x* (as a fraction of the initial investment):

- gains (x ≥ 0): v(x) = x^α
- losses (x < 0): v(x) = −λ · (−x)^β

**"Mean PT value"** = the average of v(x) over the 1,000 simulated futures. It is a **satisfaction score, not dollars**. Higher is better.

---

## 2. λ, α y β: las preguntas, explicadas fácil / λ, α and β: the questions made easy

### 2.1 λ: aversión a pérdidas / loss aversion

🇪🇸 **La pregunta:** "Lanzamos una moneda. Si sale cara pierdes el 10% de tu portafolio. Si sale sello ganas G%. ¿Cuál es la G mínima con la que aceptas jugar?"

**La lógica:**
- Una persona a la que perder y ganar le importan igual acepta con **G = 10%**. Es un juego justo: λ = 10/10 = **1**.
- Si pides **G = 20%**, una pérdida de 10% te pesa como una ganancia de 20%. Entonces λ = 20/10 = **2**: perder te duele el doble.
- **Fórmula:** λ = G ÷ pérdida.

**Por qué tres preguntas:** se repite con pérdidas de 5%, 10% y 20%, y se usa la **mediana** (el valor del medio), para que una respuesta impulsiva no domine. Si alguien responde "no aceptaría con ninguna", se le asigna el máximo, λ = 5. λ siempre queda entre 1 y 5.

**Ejemplo:** respuestas de 10%, 20% y 50% para pérdidas de 5%, 10% y 20% dan razones de 2, 2 y 2,5. La mediana es **λ = 2**.

🇬🇧 **The question:** "We flip a coin. Heads, you lose 10% of your portfolio. Tails, you win G%. What is the smallest G that makes you accept the bet?"

**The logic:**
- Someone who weighs losses and gains equally accepts with **G = 10%**. It is a fair bet: λ = 10/10 = **1**.
- If you ask for **G = 20%**, a 10% loss weighs on you like a 20% gain. So λ = 20/10 = **2**: losing hurts twice as much.
- **Formula:** λ = G ÷ loss.

**Why three questions:** we repeat it with 5%, 10% and 20% losses and take the **median**, so that one impulsive answer does not dominate. "I would not accept any of these" counts as the maximum, λ = 5. λ always stays between 1 and 5.

**Example:** answers of 10%, 20% and 50% for losses of 5%, 10% and 20% give ratios of 2, 2 and 2.5. The median is **λ = 2**.

### 2.2 α: curvatura en ganancias / curvature for gains

🇪🇸 **Qué mide, en palabras:** si prefieres "pájaro en mano". Con α = 1 cada dólar extra de ganancia te alegra igual. Con α < 1, ganar más te alegra cada vez menos, así que prefieres asegurar.

**La pregunta:** "Tienes una apuesta: 50% ganas 10%, 50% no ganas nada. ¿Por qué ganancia **segura** mínima la cambiarías?"

**La lógica:**
- La apuesta vale en promedio **5%** (la mitad de 10%).
- Si exiges 5% seguro, eres **neutral**: α = 1.
- Si aceptas **4% seguro**, renuncias a 1 punto a cambio de certeza. Prefieres asegurar: α < 1.

**Cómo sale el número:** te da igual la apuesta que el monto seguro, así que su "satisfacción" es igual: 4^α = 0,5 · 10^α. Despejando: **α = ln(0,5) ÷ ln(4/10) = 0,76**. Se pregunta con 10% y con 30% y se promedia.

🇬🇧 **What it measures:** whether you prefer "a bird in the hand". With α = 1, every extra dollar of gain pleases you the same. With α < 1, each extra gain pleases you less, so you prefer to lock in gains.

**The question:** "You hold a bet: 50% you win 10%, 50% you win nothing. What is the smallest **sure** gain you would take instead?"

**The logic:**
- The bet is worth **5%** on average (half of 10%).
- If you demand a sure 5%, you are **neutral**: α = 1.
- If you accept a **sure 4%**, you give up 1 point for certainty. You prefer to lock in gains: α < 1.

**Where the number comes from:** you are indifferent, so both give the same satisfaction: 4^α = 0.5 · 10^α. Solving: **α = ln(0.5) ÷ ln(4/10) = 0.76**. We ask with 10% and 30% stakes and average.

### 2.3 β: curvatura en pérdidas / curvature for losses

🇪🇸 **Qué mide, en palabras:** lo mismo, pero con pérdidas. Con β < 1, la segunda pérdida duele menos que la primera, así que **prefieres arriesgarte antes que aceptar una pérdida segura**. Es el típico "no vendo con pérdida, mejor espero a que se recupere".

**La pregunta:** "Debes elegir: una apuesta (50% pierdes 10%, 50% no pierdes nada) o una pérdida **segura**. ¿Cuál es la pérdida segura máxima que aceptarías?"

**La lógica:**
- La apuesta pierde en promedio 5%.
- Si aceptas hasta 5% seguro: neutral, β = 1.
- Si solo aceptas hasta **4%**, ya con un 5% seguro prefieres apostar: te arriesgas en las pérdidas, β = 0,76.

🇬🇧 **What it measures:** the same idea with losses. With β < 1, the second loss hurts less than the first, so **you prefer to gamble rather than accept a sure loss**. It is the classic "I won't sell at a loss, I'll wait for it to come back".

**The question:** "Choose between a bet (50% you lose 10%, 50% you lose nothing) or a **sure** loss. What is the largest sure loss you would accept?"

**The logic:**
- The bet loses 5% on average.
- If you accept a sure loss of up to 5%: neutral, β = 1.
- If you only accept up to **4%**, then facing a sure 5% loss you would rather gamble. You take risks with losses: β = 0.76.

📍 Fórmulas / Formulas: `estimate_profile` en / in [`core/profile.py`](../core/profile.py); notebook §3.

### 2.4 Por qué 2,25 y 0,88 / Why 2.25 and 0.88

🇪🇸 Son los valores que Tversky y Kahneman estimaron en 1992 para una persona típica. Usamos ese "cliente promedio" en el informe para que los resultados sean comparables con la literatura.

🇬🇧 These are the values Tversky and Kahneman estimated in 1992 for a typical person. We use this "average client" in the report so the results are comparable with the literature.

---

## 3. "Tú tal como eres" / "You as you are"

🇪🇸 Es **la misma inversión, pero manejada con tus hábitos reales**, los que detectó el cuestionario. Se llama así porque es un espejo: comparamos al "tú disciplinado" contra el "tú de verdad".

Para el cliente de referencia, la simulación hace dos cosas:

- **Pánico:** si el portafolio cae 20% desde su máximo, **vende todo** y pasa a efectivo. Vuelve a invertir cuando el mercado rebota 15% desde el mínimo.
- **Persecución:** cada 3 meses mueve el 25% de su dinero hacia los 3 ETFs que más subieron en el último año.

Si el cuestionario no detecta sesgos, "tú tal como eres" es igual a la regla disciplinada.

**Resultado:** la disciplina termina típicamente con US$ 326.297; "tú tal como eres", con US$ 272.656. **Tus hábitos cuestan unos US$ 53.600** (16%).

🇬🇧 It is **the same investment, managed with your real habits**, the ones the questionnaire detected. The name says it: it is a mirror comparing the "disciplined you" with the "real you".

For the reference client, the simulation does two things:

- **Panic:** if the portfolio falls 20% from its peak, it **sells everything** and moves to cash. It reinvests when the market rebounds 15% from the bottom.
- **Chasing:** every 3 months it moves 25% of the money into the 3 ETFs with the best last-12-month returns.

If no biases are detected, "you as you are" equals the disciplined rule.

**Result:** discipline typically ends with US$ 326,297; "you as you are", with US$ 272,656. **Your habits cost about US$ 53,600** (16%).

📍 Notebook §3 (`REF = Profile(panic=True, chase=True)`) y / and §8 (`costs = behavior_costs(…)`, columna / column "Costo en la mediana").

---

## 4. Rebalanceo por bandas y b\* / Band rebalancing and b\*

### 4.1 Cómo funciona / How it works

🇪🇸 **Idea:** decides unos pesos objetivo (por ejemplo 35% en tecnología) y les dejas un margen de tolerancia, la **banda**. Cada mes miras el portafolio:

- Si **todos** los activos están dentro de su banda, **no haces nada**.
- Si **alguno** se sale, vuelves **todo** el portafolio a los pesos objetivo: vendes lo que creció de más y compras lo que quedó corto.

**Ejemplo con banda b = 5 puntos y tecnología con objetivo de 35%:**
- La tecnología sube y pasa a pesar 38%. Está dentro de la banda (30% a 40%), así que no haces nada.
- Sigue subiendo y llega a 41%. Se salió, así que vendes tecnología y vuelves al 35% (y todo lo demás a su objetivo).

**Banda angosta** (2%): rebalanceas casi todos los meses, pagas muchos costos y vendes seguido a los ganadores.
**Banda ancha** (50%): casi nunca rebalanceas. Es prácticamente "comprar y mantener".

La banda se mide en **puntos porcentuales**. Con b = 50%, la tecnología tendría que pasar de 35% a **85%** del portafolio para que se dispare el rebalanceo, y eso casi nunca ocurre en 10 años.

🇬🇧 **Idea:** you choose target weights (e.g. 35% in technology) and allow a tolerance margin, the **band**. Every month you check the portfolio:

- If **every** asset is inside its band, **do nothing**.
- If **any** asset is outside, bring the **whole** portfolio back to the targets: sell what grew too much and buy what fell short.

**Example with band b = 5 points and a 35% technology target:**
- Technology rises to 38%. It is inside the band (30% to 40%), so you do nothing.
- It keeps rising to 41%. It is outside, so you sell technology back to 35% (and reset everything else).

**Narrow band** (2%): you rebalance almost every month, pay a lot of costs and keep selling the winners.
**Wide band** (50%): you almost never rebalance. It is practically "buy and hold".

The band is measured in **percentage points**. With b = 50%, technology would have to grow from 35% to **85%** of the portfolio to trigger a rebalance, which almost never happens in 10 years.

### 4.2 ¿Qué es b\*? / What is b\*?

🇪🇸 El asterisco (\*) significa **"el mejor valor encontrado"**. Probamos 10 bandas (2%, 3%, 5%, 7,5%, 10%, 15%, 20%, 25%, 35% y 50%) en 300 futuros de práctica, y elegimos la que dio el mayor valor PT medio. Ganó **b\* = 50%**, la más ancha.

**Qué significa:** con estos datos, **rebalancear no ayuda**. Si no rebalanceas, crece el peso del activo que más rindió: la tecnología pasa de 35% a 50% en el futuro típico, y el oro baja de 35% a 24%. Rebalancear obliga a vender tecnología para volver a 35%, y así te pierdes parte de su retorno. A cambio, sin rebalancear sube el riesgo. Además cada operación cuesta 0,1%.

**Cómo decirlo:** "La regla de bandas aprendió sola que, con estos datos, lo mejor es no tocar el portafolio."

Lo mismo pasa con los otros asteriscos: **θ\* = 1,25** y **N\* = 120 meses** son los mejores valores para la re-optimización anual.

🇬🇧 The asterisk (\*) means **"the best value found"**. We tried 10 bands (2%, 3%, 5%, 7.5%, 10%, 15%, 20%, 25%, 35% and 50%) on 300 practice futures and picked the one with the highest mean PT value. The winner was **b\* = 50%**, the widest.

**What it means:** with this data, **rebalancing does not help**. If you do not rebalance, the weight of the best-performing asset grows: technology goes from 35% to 50% in the typical future, and gold falls from 35% to 24%. Rebalancing forces you to sell technology back to 35%, so you miss part of its return. In exchange, without rebalancing risk rises. Each trade also costs 0.1%.

**How to say it:** "The band rule learned by itself that, with this data, the best thing is to leave the portfolio alone."

The same goes for the other asterisks: **θ\* = 1.25** and **N\* = 120 months** are the best values for annual re-optimization.

📍 Notebook §7: tablas / tables `pfa_tab` y / and `cfa_tab`; guardado en / saved in [`data/tuned_params.json`](../data/tuned_params.json).

---

## 5. El equivalente seguro: cómo se calcula / The certainty equivalent: how it is calculated

📍 Notebook §8, columna / column "Equivalente cierto (US$)" de / of `results_table`; función / function `certainty_equivalent` en / in [`core/evaluation.py`](../core/evaluation.py).

🇪🇸 **La pregunta que responde:** "¿Qué cantidad de dinero **segura** te dejaría igual de satisfecho que esta estrategia con todo su riesgo?"

**Paso a paso (comprar y mantener):**
1. En cada uno de los 1000 futuros calculamos tu ganancia: **x = (riqueza final − 100.000) ÷ 100.000**. Por ejemplo, terminar con 326.000 da x = 2,26 (ganaste 226%).
2. Convertimos cada ganancia en satisfacción con la fórmula PT: x^0,88 si ganas, −2,25·(pérdida)^0,88 si pierdes.
3. Promediamos los 1000 valores: **2,286**.
4. Buscamos la ganancia segura que da exactamente esa satisfacción: x^0,88 = 2,286, así que **x = 2,286^(1/0,88) = 2,56**, una ganancia de 256%.
5. En dinero: 100.000 + 2,56 × 100.000 = **≈ US$ 356.000**.

**Mismo cálculo para "tú tal como eres":** 1,830^(1/0,88) = 1,99, lo que da **≈ US$ 299.000**. La diferencia, unos **US$ 57.000**, es lo que te cuestan tus sesgos medido en tu propia satisfacción.

| Política | Valor PT | Equivalente seguro |
|---|---|---|
| Comprar y mantener / Bandas | 2,286 | ≈ US$ 356.000 |
| Persecución | 1,938 | ≈ US$ 312.000 |
| Re-optimización anual | 1,909 | ≈ US$ 308.000 |
| Pánico | 2,126 | ≈ US$ 336.000 |
| Tú tal como eres | 1,830 | ≈ US$ 299.000 |

**Pregunta trampa: ¿por qué 356.000 es más que la mediana (326.000) y menos que la media (363.000)?**
- **Menos que la media:** el cliente prefiere lo seguro (α < 1) y le duelen los futuros con pérdida (λ). Por eso acepta menos dinero seguro que el promedio incierto.
- **Más que la mediana:** hay algunos futuros muy buenos (hasta US$ 700.000) que suben mucho el promedio de satisfacción.

🇬🇧 **The question it answers:** "What **sure** amount of money would make you as satisfied as this strategy with all its risk?"

**Step by step (buy and hold):**
1. In each of the 1,000 futures we compute your gain: **x = (final wealth − 100,000) ÷ 100,000**. For example, ending with 326,000 gives x = 2.26 (a 226% gain).
2. We turn each gain into satisfaction with the PT formula: x^0.88 for gains, −2.25·(loss)^0.88 for losses.
3. We average the 1,000 values: **2.286**.
4. We find the sure gain with exactly that satisfaction: x^0.88 = 2.286, so **x = 2.286^(1/0.88) = 2.56**, a 256% gain.
5. In money: 100,000 + 2.56 × 100,000 = **≈ US$ 356,000**.

**Same calculation for "you as you are":** 1.830^(1/0.88) = 1.99, which gives **≈ US$ 299,000**. The difference, about **US$ 57,000**, is what your biases cost you, measured in your own satisfaction.

**Trick question: why is 356,000 above the median (326,000) but below the mean (363,000)?**
- **Below the mean:** the client prefers certainty (α < 1) and dislikes the losing futures (λ). So they accept less sure money than the uncertain average.
- **Above the median:** a few very good futures (up to US$ 700,000) raise the average satisfaction a lot.

---

## 6. Media-varianza y por qué usamos CVaR / Mean-variance and why we used CVaR

🇪🇸 **Media-varianza (Markowitz, 1952; Nobel 1990)** es el modelo clásico. Busca el mayor retorno esperado (la **media**) para un nivel dado de **varianza**, es decir, de cuánto "salta" el portafolio, para arriba o para abajo.

**El problema para nuestro cliente:** la varianza castiga **igual** una sorpresa buena (+15%) que una mala (−15%). A nuestro cliente no le molestan las subidas; le duelen las caídas, y λ dice exactamente eso.

**CVaR al 95%** mira **solo las malas noticias**:
- Ordena los meses de la historia del peor al mejor.
- Toma el **5% de los peores meses**.
- Calcula **la pérdida promedio de esos meses**.

Si el CVaR es 7,5%, entonces "en un mes realmente malo, pierdes en promedio 7,5%".

**El límite depende de λ:** límite = 10% − 8% × (λ − 1) ÷ 4. Con λ = 1 el límite es 10%; con λ = 2,25, **7,5%**; con λ = 5, **2%**. Mientras más te duele perder, menos pérdida te permite el optimizador.

**Tres razones para elegir CVaR:**
1. **Mide lo que le duele al cliente:** las caídas, no las subidas.
2. **Es lineal**, así que Gurobi lo resuelve en segundos aunque haya decisiones de sí/no.
3. **Se conecta fácil con λ.**

**VaR frente a CVaR:** el VaR 95% es "el umbral" del peor 5% ("en 1 de cada 20 meses pierdes al menos X"). El CVaR es "el promedio de lo que pasa más allá de ese umbral". El CVaR es más prudente porque mira qué tan malo es lo malo.

🇬🇧 **Mean-variance (Markowitz, 1952; Nobel 1990)** is the classic model. It looks for the highest expected return (the **mean**) for a given **variance**, that is, how much the portfolio "jumps" up or down.

**The problem for our client:** variance penalizes a good surprise (+15%) **the same** as a bad one (−15%). Our client does not mind upswings; they are hurt by drops, and λ says exactly that.

**CVaR at 95%** looks **only at the bad news**:
- Sort the historical months from worst to best.
- Take the **worst 5% of months**.
- Compute **the average loss in those months**.

If CVaR is 7.5%, then "in a really bad month, you lose 7.5% on average".

**The limit depends on λ:** limit = 10% − 8% × (λ − 1) ÷ 4. With λ = 1 the limit is 10%; with λ = 2.25, **7.5%**; with λ = 5, **2%**. The more losses hurt you, the less loss the optimizer allows.

**Three reasons to choose CVaR:**
1. **It measures what hurts the client:** drops, not rallies.
2. **It is linear**, so Gurobi solves it in seconds even with yes/no decisions.
3. **It connects easily with λ.**

**VaR versus CVaR:** the 95% VaR is the "threshold" of the worst 5% ("in 1 month out of 20 you lose at least X"). CVaR is "the average of what happens beyond that threshold". CVaR is more prudent because it looks at how bad the bad cases are.

---

## 7. Las reglas del asesor / The advisor's rules

🇪🇸 Son las **restricciones** del optimizador: reglas de sentido común que pone un asesor. En el dashboard se cambian en la barra lateral.

| Regla | Valor | Qué significa | Por qué existe |
|---|---|---|---|
| Invertir todo | Σw = 100% | Los pesos suman 100% | Todo el dinero queda asignado (el efectivo, BIL, también es un activo) |
| Sin ventas en corto | w ≥ 0 | No se apuesta a la baja | Un cliente minorista no vende acciones prestadas |
| **Máximo de activos (K)** | **8** | Máximo 8 ETFs | Un portafolio simple de seguir y con menos comisiones |
| **Posición mínima (l)** | **5%** | Si un ETF entra, con al menos 5% | Evita posiciones diminutas que no aportan (US$ 500 de US$ 100.000 no mueven nada) |
| **Posición máxima (u)** | **35%** | Ningún ETF pasa de 35% | No poner todos los huevos en una canasta |
| **Tope por clase** | **50%** | Máximo 50% por clase de activo | Diversificar entre tipos de activos, no solo entre ETFs |
| Límite de riesgo | CVaR ≤ límite(λ) | Pérdida promedio en meses malos acotada | Respeta la aversión a pérdidas del cliente |

**Las 5 clases de activos:** acciones de EE.UU. (9 sectores), acciones internacionales (4), renta fija (6), activos reales (bienes raíces, oro, plata y materias primas: 4) y efectivo (1). En total, 24 ETFs.

**Por qué es MILP:** las reglas "máximo 8 activos" y "mínimo 5% si entra" necesitan una variable de **sí/no** por ETF (z = 1 si entra, 0 si no). Las variables enteras convierten el modelo lineal en *entero mixto*.

**Un detalle importante:** en el portafolio de referencia, **los dos topes de clase están activos**:
- acciones de EE.UU. = XLK 35% + XLV 10% + XLY 5% = **50%**;
- activos reales = GLD 35% + SLV 8,7% + VNQ 6,3% = **50%**.

Y XLK y GLD tocan el máximo de 35%. Sin las reglas del asesor, el optimizador habría puesto 64% en tecnología, 23% en oro y 12% en salud. **Las reglas son las que evitan un portafolio todavía más concentrado.**

🇬🇧 These are the optimizer's **constraints**: common-sense rules an advisor would impose. In the dashboard you change them in the sidebar.

| Rule | Value | What it means | Why it exists |
|---|---|---|---|
| Fully invested | Σw = 100% | Weights add up to 100% | All money is allocated (cash, BIL, is also an asset) |
| No short selling | w ≥ 0 | No betting on prices falling | A retail client does not sell borrowed shares |
| **Max number of assets (K)** | **8** | At most 8 ETFs | A portfolio that is easy to follow, with fewer fees |
| **Minimum position (l)** | **5%** | If an ETF is included, at least 5% | Avoids tiny positions that add nothing |
| **Maximum position (u)** | **35%** | No ETF above 35% | Don't put all your eggs in one basket |
| **Class cap** | **50%** | At most 50% per asset class | Diversify across asset types, not just across ETFs |
| Risk limit | CVaR ≤ limit(λ) | Average loss in bad months is capped | Respects the client's loss aversion |

**The 5 asset classes:** US equities (9 sectors), international equities (4), fixed income (6), real assets (real estate, gold, silver and commodities: 4) and cash (1). 24 ETFs in total.

**Why it is a MILP:** the rules "at most 8 assets" and "at least 5% if included" need a **yes/no** variable per ETF (z = 1 if included, 0 if not). Integer variables turn the linear model into a *mixed-integer* one.

**An important detail:** in the reference portfolio **both class caps are binding**:
- US equities = XLK 35% + XLV 10% + XLY 5% = **50%**;
- real assets = GLD 35% + SLV 8.7% + VNQ 6.3% = **50%**.

XLK and GLD also hit the 35% maximum. Without the advisor's rules, the optimizer would have put 64% in technology, 23% in gold and 12% in health care. **The rules are what prevent an even more concentrated portfolio.**

---

📍 Notebook §4: celda / cell `port_ref = build_portfolio(REF, rets, CONS)`; restricciones / constraints `Constraints` en / in [`core/portfolio.py`](../core/portfolio.py).

---

## 8. Las clases de políticas de Powell (PFA, CFA, VFA, DLA) / Powell's policy classes

🇪🇸 Una **política** es una forma de decidir cada mes qué hacer. Powell dice que todas las políticas caen en 4 familias:

| Clase | Idea sencilla | Analogía | ¿La usamos? |
|---|---|---|---|
| **PFA** | Una **regla fija**: "si pasa X, haz Y" | "Si el tanque baja de un cuarto, echo gasolina" | ✅ Rebalanceo por bandas (y las conductuales) |
| **CFA** | Un **optimizador** que se vuelve a correr, con **perillas** que lo corrigen | "Cada año rehago mi presupuesto, pero dejo un margen extra de seguridad" | ✅ Re-optimización anual |
| **VFA** | Estimar **cuánto vale el futuro** desde cada situación | Un jugador de ajedrez que sabe cuánto vale cada posición | ❌ |
| **DLA** | **Simular hacia adelante** antes de cada decisión | Un GPS que recalcula toda la ruta en cada esquina | ❌ |

**La CFA en nuestro proyecto:** cada 12 meses vuelve a correr el MILP con los últimos **N** meses de datos y reajusta el portafolio. Tiene dos perillas:
- **θ (theta):** multiplica el límite de riesgo. θ = 1,25 permite 25% más de riesgo de cola que el límite base.
- **N:** cuántos meses de historia mira (36, 60 o 120).

Ganó **θ\* = 1,25 y N\* = 120**. En la evaluación principal, la CFA fue **la peor regla disciplinada**: rota 48% al año y tiene la caída típica más grande (29,6%). Pero esa evaluación arma el portafolio con la misma historia de la que sortea los futuros, y eso favorece a comprar y mantener. **En la prueba fuera de muestra, la CFA le ganó a comprar y mantener en las tres fechas de corte.**

**Por qué no usamos VFA ni DLA:** el estado tiene 24 pesos más 12 meses de historia. Estimar el valor del futuro sobre algo tan grande (VFA), o simular hacia adelante en cada mes de cada uno de los 1000 escenarios (DLA), era demasiado costoso y difícil de explicar a un cliente.

🇬🇧 A **policy** is a way of deciding what to do each month. Powell says every policy belongs to one of 4 families:

| Class | Simple idea | Analogy | Used? |
|---|---|---|---|
| **PFA** | A **fixed rule**: "if X happens, do Y" | "When the tank drops below a quarter, refuel" | ✅ Band rebalancing (and the behavioral ones) |
| **CFA** | An **optimizer** re-run over time, with **knobs** that correct it | "Every year I redo my budget, but keep an extra safety margin" | ✅ Annual re-optimization |
| **VFA** | Estimate **what the future is worth** from each situation | A chess player who knows the value of each position | ❌ |
| **DLA** | **Simulate ahead** before each decision | A GPS that recomputes the whole route at every corner | ❌ |

**The CFA in our project:** every 12 months it re-runs the MILP with the last **N** months of data and rebalances to the new solution. It has two knobs:
- **θ (theta):** scales the risk limit. θ = 1.25 allows 25% more tail risk than the base limit.
- **N:** how many months of history it uses (36, 60 or 120).

The winners were **θ\* = 1.25 and N\* = 120**. In the main evaluation the CFA was **the worst disciplined rule**: it turns over 48% a year and has the largest typical drawdown (29.6%). But that evaluation builds the portfolio with the same history the futures are drawn from, which favors buy and hold. **In the out-of-sample test, the CFA beat buy and hold at all three cut dates.**

**Why no VFA or DLA:** the state has 24 weights plus 12 months of history. Estimating the value of the future over something that large (VFA), or simulating ahead at every month of each of the 1,000 scenarios (DLA), was too costly and hard to explain to a client.

---

## 9. Ideas clave / Key ideas

| 🇪🇸 Español | 🇬🇧 English |
|---|---|
| Tu comportamiento cuesta caro: 16% de tu resultado típico. | Your behavior is expensive: 16% of your typical result. |
| Comprar y mantener empata con la mejor banda (50%) y es más simple; si el mercado cambia, conviene re-optimizar. | Buy and hold ties with the best band (50%) and is simpler; if the market changes, re-optimizing pays off. |
| El pánico y la persecución le cuestan al cliente de referencia unos US$ 53.600 en 10 años. | Panic selling and chasing cost the reference client about US$ 53,600 over 10 years. |
| El valor PT es satisfacción, no dólares; en dólares seguros equivale a US$ 356.000. | The PT value is satisfaction, not dollars; in sure dollars it equals US$ 356,000. |
| b\* = 50% significa que, con estos datos, lo mejor es no tocar el portafolio. | b\* = 50% means that, with this data, the best move is to leave the portfolio alone. |
| Usamos CVaR porque al cliente le duelen las caídas, no las subidas. | We used CVaR because the client is hurt by drops, not by rallies. |
| Todas las reglas se probaron en los mismos 1000 futuros: la diferencia es la regla, no la suerte. | Every rule was tested on the same 1,000 futures: the difference is the rule, not luck. |
| Ajustamos con unos futuros y evaluamos con otros, para no hacernos trampa. | We tuned on some futures and evaluated on others, so we don't fool ourselves. |
| Espera ver tu portafolio caer alrededor de 21% en algún momento: es parte del plan. | Expect to see your portfolio drop about 21% at some point: it is part of the plan. |
| Vender en pánico deja peor en 46% de los futuros y mejor en 7%. | Panic selling ends worse in 46% of the futures and better in 7%. |
