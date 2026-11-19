"""Interfaz pública del proyecto: perfil → portafolio → evaluación de políticas."""
from .data import UNIVERSE, NAMES, ASSET_CLASSES, CASH, load_returns
from .profile import Profile, estimate_profile, describe_profile, pt_value, DEFAULT_ANSWERS
from .portfolio import Constraints, Portfolio, build_portfolio, cvar_limit, hist_cvar, class_matrix
from .scenarios import Scenarios, block_bootstrap, TUNE_SEED, EVAL_SEED, HORIZON
from .policies import (BuyAndHold, BandRebalancing, AnnualReoptimization, PanicSelling, PerformanceChasing,
                       standard_policies, BH, PFA, CFA, PANIC, CHASE, CLIENT)
from .simulator import simulate, SimResult
from .evaluation import (evaluate, results_table, paired_comparison, behavior_costs, summarize, pt_scores,
                         fan_quantiles, tune, recommend, plain_language, usd)
