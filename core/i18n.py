"""Nombres en español e inglés. Las políticas, clases y activos se identifican internamente en español;
estas funciones solo cambian cómo se muestran."""

LANGS = {"es": "Español", "en": "English"}

POLICY_EN = {
    "Comprar y mantener": "Buy and hold",
    "Rebalanceo por bandas": "Band rebalancing",
    "Re-optimización anual": "Annual re-optimization",
    "Venta por pánico": "Panic selling",
    "Persecución de rendimiento": "Performance chasing",
    "Tú tal como eres": "You as you are",
}
KLASS_EN = {"Conductual": "Behavioral", "Conductual (perfil)": "Behavioral (profile)"}
CLASS_EN = {
    "Acciones EE.UU.": "US equities", "Acciones internacionales": "International equities",
    "Renta fija": "Fixed income", "Activos reales": "Real assets", "Efectivo": "Cash",
}
NAMES_EN = {
    "XLK": "US technology", "XLF": "US financials", "XLV": "US health care", "XLE": "US energy",
    "XLI": "US industrials", "XLY": "US consumer discretionary", "XLP": "US consumer staples",
    "XLU": "US utilities", "XLB": "US materials", "EFA": "Developed markets ex-US", "EEM": "Emerging markets",
    "VGK": "Europe", "EWJ": "Japan", "TLT": "US Treasuries 20+ years", "IEF": "US Treasuries 7-10 years",
    "SHY": "US Treasuries 1-3 years", "LQD": "Investment-grade corporate bonds", "HYG": "High-yield bonds",
    "TIP": "Inflation-linked bonds", "VNQ": "Real estate (REITs)", "GLD": "Gold", "SLV": "Silver",
    "DBC": "Commodities", "BIL": "Treasury bills 1-3 months (cash)",
}


def policy_name(name, lang="es"):
    return POLICY_EN.get(name, name) if lang == "en" else name


def klass_name(name, lang="es"):
    return KLASS_EN.get(name, name) if lang == "en" else name


def class_name(name, lang="es"):
    return CLASS_EN.get(name, name) if lang == "en" else name


def asset_name(ticker, lang="es"):
    from .data import NAMES
    return NAMES_EN.get(ticker, ticker) if lang == "en" else NAMES.get(ticker, ticker)
