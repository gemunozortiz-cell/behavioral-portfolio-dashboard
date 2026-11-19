# 04: PFA de rebalanceo por bandas y arnés de ajuste

**What to build:** La política de bandas, más un arnés genérico de búsqueda en cuadrícula que corre sobre los escenarios de ajuste (300) y devuelve el valor PT medio, con su error estándar, para cada valor de b. Se elige b* y se guarda.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] Política con interfaz común (estado → pesos después de operar), clase "PFA" y parámetro b
- [ ] Cuadrícula b ∈ {2, 3, 5, 7.5, 10, 15, 20}%; gráfico del valor PT frente a b con barras de error
- [ ] Tests: b muy grande da lo mismo que comprar y mantener; con b = 0 los costos valen 10 pb × valor operado
- [ ] b* queda guardado en el JSON de parámetros ajustados
