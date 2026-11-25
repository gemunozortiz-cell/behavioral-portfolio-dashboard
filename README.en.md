# Behavioral portfolio dashboard

🌐 **English** · [Español](README.md)

[![Open the dashboard](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://dashboard-portafolio-conductual.streamlit.app/?lang=en)

A tool that lets a financial advisor do three things with a client:

1. **Profile them** with an 11-question questionnaire that estimates their prospect-theory parameters (loss aversion λ and curvatures α, β) and detects two biases: panic selling and performance chasing.
2. **Build their portfolio** with a mean-CVaR MILP solved with Gurobi, whose tail-risk limit depends on λ.
3. **Show them what their own behavior costs** over 10 years, simulating month by month with Powell's framework and comparing disciplined rules with rules that mimic their biases.

👉 **[Open the dashboard in English](https://dashboard-portafolio-conductual.streamlit.app/?lang=en)**. It runs in the browser, also on a phone, with nothing to install. The selector at the top of the sidebar switches between Spanish and English.

👉 **[See the full notebook with results](portafolio_conductual.ipynb)**. GitHub renders it with all its tables and charts. Every text cell is written in Spanish and then in English; the tables it prints use Spanish column names, translated below.

👉 **[Concepts explained simply (Spanish and English)](docs/GUIDE_ES_EN.md)**: PT, λ, α, β, certainty equivalent, bands and b\*, CVaR versus mean-variance, PFA/CFA and the advisor's rules.

---

## What is in this repository

| Path | Content |
|---|---|
| [`Report_EN.md`](Report_EN.md) · [`Informe_ES.md`](Informe_ES.md) | The report without code, in English and Spanish: Powell model, policies, evaluation and recommendation. |
| [`portafolio_conductual.ipynb`](portafolio_conductual.ipynb) | The full report: data, Powell model, questionnaire, MILP, simulator, policies, tuning, evaluation, sensitivity and recommendation. It includes the tests (`assert`). |
| [`app.py`](app.py) | The Streamlit dashboard (Spanish and English). |
| [`core/`](core) | The logic shared by the notebook and the app: `profile` (questionnaire), `portfolio` (MILP), `scenarios` (bootstrap), `policies`, `simulator`, `evaluation`, `plots` and `i18n` (English names). |
| [`data/`](data) | Monthly returns of the 24 ETFs (2008-01 to 2026-10) and the tuned parameters. |
| [`docs/GUIDE_ES_EN.md`](docs/GUIDE_ES_EN.md) | Bilingual guide to the concepts and results. |
| [`docs/SPEC.md`](docs/SPEC.md) | Specification: user stories and design decisions (Spanish). |
| [`docs/tickets/`](docs/tickets) | The work plan in 9 tickets (Spanish). |

The notebook writes `core/` and `app.py` with `%%writefile` cells, so the report and the app use exactly the same code.

## The problem in Powell's framework

- **State** $S_t$: wealth, current weights, wealth peak (to measure drawdowns), the last 12 months of returns and each policy's own memory.
- **Decision** $x_t$: the amounts bought or sold each month, with no short positions.
- **Exogenous information**: the month's returns, drawn with a circular block bootstrap of 3 to 6 months over the real history.
- **Transition**: wealth evolves with the returns and pays a 10 bp cost on the traded value.
- **Objective**: maximize $\mathbb{E}[v((W_T - W_{ref})/W_0)]$, where $v$ is the prospect-theory value function.

The full equations, the units and what is known at each decision are in section 2 of the notebook.

## Policies compared

| Policy | Class | Tunable parameters |
|---|---|---|
| Buy and hold | Baseline | — |
| Band rebalancing | PFA | band width $b$ |
| Annual re-optimization (re-solves the MILP every 12 months) | CFA | risk factor $\theta$, window $N$ |
| Panic selling | Behavioral | $d, r, \varphi$ (from the questionnaire) |
| Performance chasing | Behavioral | $\kappa, f$ (from the questionnaire) |
| You as you are (the detected biases) | Behavioral | — |

Tuning uses 300 scenarios with seed 2026 (150 for the CFA). The final evaluation uses **1,000 scenarios with a different seed (7777)**. All policies are simulated on the same scenarios (common random numbers).

## Results (reference client: λ = 2.25, α = β = 0.88, with both biases)

Initial wealth US$ 100,000, 10 years, 1,000 evaluation scenarios. Source: notebook section 8, the `results_table(results, REF, W0)` cell.

| Policy | Mean PT value [95% CI] | Certainty equivalent | Final wealth P5 | Median | P95 | Median max. drawdown |
|---|---|---|---|---|---|---|
| Buy and hold | 2.286 [2.202, 2.371] | US$ 355,928 | US$ 151,370 | US$ 326,297 | US$ 703,185 | 20.8% |
| Band rebalancing (b* = 50%) | 2.287 [2.202, 2.371] | US$ 355,966 | US$ 151,370 | US$ 326,297 | US$ 703,185 | 20.8% |
| Annual re-optimization (θ* = 1.25, N* = 120) | 1.909 [1.813, 2.005] | US$ 308,474 | US$ 112,667 | US$ 269,775 | US$ 701,073 | 29.6% |
| Panic selling | 2.126 [2.040, 2.213] | US$ 335,678 | US$ 133,340 | US$ 304,734 | US$ 699,368 | 20.9% |
| Performance chasing | 1.938 [1.866, 2.010] | US$ 312,090 | US$ 141,501 | US$ 289,581 | US$ 601,939 | 19.8% |
| You as you are (panic + chasing) | 1.830 [1.755, 1.905] | US$ 298,683 | US$ 127,025 | US$ 272,656 | US$ 599,908 | 19.8% |

**How to read it.** The PT value is a satisfaction score, not dollars. The **certainty equivalent** turns it into dollars: it is the sure amount the client values as much as the policy with all its risk. For example, buy and hold is worth as much to this client as about US$ 356,000 for sure in 10 years; "you as you are" is worth about US$ 299,000.

**Recommendation: buy and hold the MILP portfolio.**
- **It cannot be told apart from the band rule.** The 95% CI of the paired PT-value difference, [−0.0009, 0.0003], includes 0, and buy and hold is simpler. The optimal band width ended at the top of the grid: with this data, rebalancing adds no value. Without rebalancing, the weight of the highest-return asset grows (XLK goes from 35% to a median of 50%; gold falls from 35% to 24%), and the objective barely penalizes the extra risk, because only 0.4% of the futures end in a loss.
- **Re-optimizing every year is significantly worse in this evaluation.** Note: the evaluation builds the portfolio with the same history the futures are drawn from, which favors buy and hold (see the out-of-sample test).
- **Behavior is expensive.** With both biases, the reference client loses **US$ 53,641 at the median** (16%) compared with discipline (95% CI of the mean cost: US$ 53,240 to 61,201) and ends worse in 86% of the scenarios. Performance chasing (US$ 36,716) costs more than panic selling (US$ 21,563).

**When it would change:**
- With λ = 1, λ = 4, 50 bp costs or a 4% annual goal, the recommendation did not change in the sensitivity analysis.
- It would change if the client cannot follow the rule during drops: then discipline is the priority, not the rule.
- **It changes if the future does not look like the history used to build the portfolio.** In the out-of-sample test (portfolio built with data before the cut, 300 futures drawn from the data after it), annual re-optimization beats buy and hold at all three cuts:

  | Cut | Buy and hold (PT · median) | Re-optimization (θ*, N*) | Untuned re-optimization (θ = 1, N = 60) |
  |---|---|---|---|
  | 2014-12 | 1.320 · US$ 221,312 | 1.947 · US$ 285,061 | 1.980 · US$ 294,196 |
  | 2017-12 | 2.114 · US$ 290,625 | 2.669 · US$ 340,271 | 3.018 · US$ 384,065 |
  | 2019-12 | 1.984 · US$ 272,143 | 3.271 · US$ 415,158 | 3.639 · US$ 445,248 |

- **Risk rises if it is never reviewed.** After 10 years, buy and hold's weights exceed the client's CVaR limit in 79% of the futures (median 7.85% versus 7.50%). A yearly review is advisable.

## Where each result comes from

Every number in this README and in the report is printed by a notebook cell. The table says which one, which `core` function computes it and which file stores it.

| Result | Notebook: section and cell | Function | Saved in |
|---|---|---|---|
| 24 ETFs, 226 monthly returns (2008-01 to 2026-10) | §1, the cell `from core.data import …` | `download_prices`, `monthly_returns` ([`core/data.py`](core/data.py)) | [`data/monthly_returns.csv`](data/monthly_returns.csv) |
| Return, volatility and best/worst month per ETF | §1, the `summary` table | — | — |
| Profile from the default answers (λ = 2, α = β = 0.76) | §3, the cell `example = estimate_profile(DEFAULT_ANSWERS)` | `estimate_profile` ([`core/profile.py`](core/profile.py)) | — |
| Reference client (λ = 2.25, α = β = 0.88, both biases) | §3, the cell `REF = Profile(panic=True, chase=True)` | `Profile` | `data/tuned_params.json` (`reference_profile`) |
| Reference portfolio (XLK 35%, GLD 35%, …), 13.42% return, 7.50% CVaR | §4, the cell `port_ref = build_portfolio(REF, rets, CONS)` | `build_portfolio` ([`core/portfolio.py`](core/portfolio.py)) | — |
| λ → CVaR limit, return and number of assets (λ = 1, 2.25, 4, 5) | §4, the `frontier` table in the cell "Pruebas del MILP" | `build_portfolio`, `cvar_limit` | — |
| b* = 50%, PT value and costs for each band | §7, the `pfa_tab = tune(…)` table and chart | `tune` ([`core/evaluation.py`](core/evaluation.py)) | [`data/tuned_params.json`](data/tuned_params.json) |
| θ* = 1.25, N* = 120 and the CFA heat map | §7, the `cfa_tab = tune(…)` table and chart | `tune` | `data/tuned_params.json` |
| Main table: PT value, CI, certainty equivalent, P5/P50/P95, drawdown, costs, turnover | §8, the `table = results_table(results, REF, W0)` cell | `results_table`, `certainty_equivalent` | — |
| Paired differences against the bands (CI [−0.0009, 0.0003]) and probability of beating them | §8, the `paired = paired_comparison(…)` table | `paired_comparison` | — |
| Cost of each behavior (US$ 53,641 at the median, 86% of scenarios) | §8, the `costs = behavior_costs(…)` table | `behavior_costs` | — |
| Fan chart and final-wealth box plot | §8, the `fan_figure` / `terminal_figure` cell | [`core/plots.py`](core/plots.py) | — |
| Sensitivity (λ = 1, λ = 4, 50 bp, 4% goal) | §9, the `sens` table | `recommend` | — |
| Diagnostics: futures in loss (0.4%), weight drift, final CVaR (79% above the limit) | §9, the `# Diagnóstico` cell | `pt_scores`, `hist_cvar` | — |
| Out-of-sample test (three cuts) | §9, the `oos` table | `evaluate`, `summarize` | — |
| Final recommendation and when it would change | §9, the cell `rec = recommend(results, REF, W0, W0, CANDIDATES)` | `recommend` | — |

**The dashboard's numbers are different on purpose.** The app simulates **500** scenarios (seed 7777) for **whoever answers the questionnaire** (by default λ = 2, α = β = 0.76 and no biases), so its amounts do not match the report's reference client. The functions and the recommendation rule are the same.

## How to use the dashboard

1. **Questionnaire:** answer the 11 questions and press *Compute my profile*.
2. **My portfolio:** what to buy today and how much, by asset class, and the typical loss in bad months.
3. **My future:** a fan chart of 500 simulated futures, with discipline and "you as you are".
4. **Compare rules:** the recommendation, the money cost of each bias and the comparison in plain sentences.

In the sidebar you change the language, the initial wealth and the goal. The advisor can adjust the maximum number of assets, the minimum and maximum positions, the class cap, λ, α, β and the biases.

## How to reproduce it on your computer

Requires Python 3.12.

```bash
git clone https://github.com/gemunozortiz-cell/dashboard-portafolio-conductual.git
cd dashboard-portafolio-conductual
python -m venv .venv
# Windows: .venv\Scripts\activate    ·    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py                 # the dashboard
jupyter notebook portafolio_conductual.ipynb   # the report (requires: pip install notebook)
```

Running the full notebook takes about 20 minutes. It downloads the data again with yfinance and regenerates `core/`, `app.py` and `data/`. Gurobi works with the restricted license that comes with `pip install gurobipy`: the largest model has about 275 variables, within the limit.

## Limitations

- The bootstrap and the MILP use the same history (2008–2026), so the results reflect that period, which was very good for technology (XLK: 18.6% a year).
- In the out-of-sample test the futures come from a short period (82 to 142 months), which favors the CFA.
- θ* and N* ended at the edge of their grid.
- The questionnaire has not been validated with real people.
- Taxes, contributions, withdrawals, inflation and cumulative prospect theory's probability weighting are not modeled.
- It is an educational tool, not investment advice.
