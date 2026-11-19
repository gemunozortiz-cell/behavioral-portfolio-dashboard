# 01: Datos, escenarios y baseline de punta a punta

**What to build:** El notebook descarga los 24 ETFs, los convierte a retornos mensuales, genera escenarios con bootstrap por bloques y simula "comprar y mantener" (con pesos iguales mientras no exista el MILP) a 10 años, mostrando el gráfico de abanico de la riqueza. Es la primera bala trazadora: datos → escenarios → simulador → gráfico.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] 24 ETFs en 5 clases de activo, retornos mensuales desde 2008-01 hasta el último mes completo, guardados en disco
- [ ] Bootstrap circular por bloques (longitud 3–6 meses, filas completas); misma semilla → mismo tensor
- [ ] Semilla de ajuste ≠ semilla de evaluación (300 y 1000 escenarios)
- [ ] El simulador aplica la transición del spec (costo de 10 pb sobre el valor operado, deriva de pesos, máximo de riqueza)
- [ ] Con retornos cero, comprar y mantener termina en W0·(1 − 0.001)
- [ ] Gráfico de abanico (P5–P25–P50–P75–P95) de la riqueza
