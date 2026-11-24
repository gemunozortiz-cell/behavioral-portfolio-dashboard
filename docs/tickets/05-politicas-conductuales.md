# 05: Políticas conductuales y costo de cada sesgo

**What to build:** La venta por pánico, la persecución de rendimiento y "Tú tal como eres" (que combina los sesgos detectados), todas aplicadas encima de la PFA con b*. El notebook muestra cuánto cuesta cada sesgo: la diferencia en la mediana de riqueza final frente a la PFA, en los mismos escenarios.

**Blocked by:** 02, 04

**Status:** ready-for-agent

- [ ] Pánico: cuando la caída llega a d vende una fracción φ a BIL y vuelve a invertir cuando el mercado (índice del portafolio w*) rebota r desde su mínimo; el pico de referencia se reinicia al volver
- [ ] Persecución: cada f meses lleva el objetivo a (1 − κ)·w* + κ·(los 3 activos con mejor retorno a 12 meses)
- [ ] Tests: pánico con d = 100% y persecución con κ = 0 dan lo mismo que la PFA
- [ ] Tabla de costo por sesgo: mediana, media con IC y % de escenarios peores que la disciplina
