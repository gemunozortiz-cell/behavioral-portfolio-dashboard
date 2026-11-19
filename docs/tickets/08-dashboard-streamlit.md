# 08: Dashboard de Streamlit

**What to build:** Una app que el cliente usa sin ver código. Llena el cuestionario y ve su perfil, su portafolio con los montos a comprar, el gráfico de abanico de su riqueza a 10 años, el costo en dinero de sus sesgos y la recomendación en lenguaje simple. El asesor puede mover K, l, u, el tope por clase, λ, α, β y los sesgos.

**Blocked by:** 07

**Status:** ready-for-agent

- [ ] El notebook genera la app con `%%writefile` y usa el mismo módulo `core`
- [ ] Carga los retornos y los parámetros ajustados guardados (sin yfinance en vivo)
- [ ] MILP y simulación con 500 escenarios en vivo y en caché; la CFA se calcula al pulsar un botón
- [ ] 4 pestañas: Cuestionario, Mi portafolio, Mi futuro, Comparar reglas
- [ ] Instrucciones para lanzarla en Colab (túnel) y en local
