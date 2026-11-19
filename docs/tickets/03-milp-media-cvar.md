# 03: Portafolio MILP media-CVaR ligado a λ

**What to build:** Dado un perfil, Gurobi elige los pesos y los activos del portafolio maximizando el retorno esperado con CVaR95 ≤ c(λ), con K activos como máximo, posiciones mínima y máxima, y un tope por clase de activo. El portafolio resultante reemplaza los pesos iguales del baseline.

**Blocked by:** 01, 02

**Status:** ready-for-agent

- [ ] Rockafellar–Uryasev sobre los meses históricos; funciona con la licencia restringida de pip
- [ ] c(λ) va de 10% (λ = 1) a 2% (λ = 5), multiplicado por θ
- [ ] Si el problema es infactible, cae a mínimo CVaR y lo informa
- [ ] Tests: Σw = 1, w ≥ 0, Σz ≤ K, l ≤ w ≤ u, topes por clase, CVaR ex post ≤ c(λ); la media no sube al subir λ
- [ ] Tabla del portafolio (activo, nombre, clase, peso) con su retorno esperado anual y su CVaR
