# 07: Evaluación final, sensibilidad y recomendación

**What to build:** Todas las políticas corren sobre los mismos 1000 escenarios de la semilla de evaluación. El notebook reporta media, desviación estándar, P5/P95 e IC95% (normal y bootstrap) del valor PT y de la riqueza final, las diferencias pareadas frente a la PFA, la sensibilidad (λ, costos, punto de referencia) y la recomendación con las condiciones en que cambiaría.

**Blocked by:** 05, 06

**Status:** ready-for-agent

- [ ] Números aleatorios comunes: un solo tensor de evaluación para todas las políticas
- [ ] Tabla de resultados, tabla pareada, gráfico de abanico y diagrama de caja de la riqueza final
- [ ] Sensibilidad: λ ∈ {1, 2.25, 4}, costos ∈ {10, 50} pb, referencia ∈ {W0, meta del 4% anual}
- [ ] Regla de recomendación: mayor valor PT medio; si el IC de la diferencia contiene 0, se elige la política más simple
- [ ] Texto de la recomendación generado a partir de los resultados
