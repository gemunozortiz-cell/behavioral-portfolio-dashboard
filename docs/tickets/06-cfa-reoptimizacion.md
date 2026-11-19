# 06: CFA de re-optimización anual y su ajuste

**What to build:** Una política que, cada 12 meses, vuelve a resolver el MILP con el límite c(λ)·θ sobre una ventana de los últimos N meses (historia previa más meses simulados) y lleva el portafolio a la nueva solución. θ y N se ajustan con el arnés del ticket 04.

**Blocked by:** 04

**Status:** ready-for-agent

- [ ] Cuadrícula θ ∈ {0.75, 1, 1.25} × N ∈ {36, 60, 120} sobre 150 escenarios de ajuste; mapa de calor del valor PT
- [ ] Test: con θ = 1 y la ventana completa, los pesos en t = 0 son los de la Parte 2
- [ ] Test: el simulador no modifica el tensor de escenarios
- [ ] θ* y N* quedan guardados en el JSON; se reporta el tiempo de cómputo
