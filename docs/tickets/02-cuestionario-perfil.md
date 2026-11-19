# 02: Cuestionario → perfil de prospect theory

**What to build:** A partir de las 11 respuestas del cuestionario, el notebook obtiene el perfil del cliente (λ, α, β, λ corregido por curvatura, y los parámetros de sesgo d, r, φ, κ, f), lo describe en frases simples y calcula el valor de prospect theory v(x).

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Las preguntas (textos y opciones) están definidas como datos que comparten el notebook y la app
- [ ] λ = mediana de G/L de 3 loterías (L = 5, 10, 20%), acotada a [1, 5]; "nunca" cuenta como 5
- [ ] α y β = ln(0.5)/ln(CE/premio), promedio de dos preguntas, acotados a [0.2, 1]
- [ ] Las 4 preguntas de sesgo se traducen a parámetros según la tabla del spec
- [ ] Tests: respuestas neutrales al riesgo dan α = β = λ = 1; el valor de v(x) es correcto en ganancias y en pérdidas
