"""Datos: universo de ETFs, descarga con yfinance y retornos mensuales."""
import numpy as np
import pandas as pd

UNIVERSE = {
    # Acciones de EE.UU. por sector
    "XLK": "Acciones EE.UU.", "XLF": "Acciones EE.UU.", "XLV": "Acciones EE.UU.",
    "XLE": "Acciones EE.UU.", "XLI": "Acciones EE.UU.", "XLY": "Acciones EE.UU.",
    "XLP": "Acciones EE.UU.", "XLU": "Acciones EE.UU.", "XLB": "Acciones EE.UU.",
    # Acciones internacionales
    "EFA": "Acciones internacionales", "EEM": "Acciones internacionales",
    "VGK": "Acciones internacionales", "EWJ": "Acciones internacionales",
    # Renta fija
    "TLT": "Renta fija", "IEF": "Renta fija", "SHY": "Renta fija",
    "LQD": "Renta fija", "HYG": "Renta fija", "TIP": "Renta fija",
    # Activos reales
    "VNQ": "Activos reales", "GLD": "Activos reales", "SLV": "Activos reales", "DBC": "Activos reales",
    # Efectivo
    "BIL": "Efectivo",
}

NAMES = {
    "XLK": "Tecnología EE.UU.", "XLF": "Financiero EE.UU.", "XLV": "Salud EE.UU.",
    "XLE": "Energía EE.UU.", "XLI": "Industrial EE.UU.", "XLY": "Consumo discrecional EE.UU.",
    "XLP": "Consumo básico EE.UU.", "XLU": "Servicios públicos EE.UU.", "XLB": "Materiales EE.UU.",
    "EFA": "Desarrollados ex-EE.UU.", "EEM": "Mercados emergentes", "VGK": "Europa", "EWJ": "Japón",
    "TLT": "Bonos del Tesoro 20+ años", "IEF": "Bonos del Tesoro 7-10 años", "SHY": "Bonos del Tesoro 1-3 años",
    "LQD": "Bonos corporativos grado de inversión", "HYG": "Bonos de alto rendimiento",
    "TIP": "Bonos indexados a inflación", "VNQ": "Bienes raíces (REITs)", "GLD": "Oro", "SLV": "Plata",
    "DBC": "Materias primas", "BIL": "Letras del Tesoro 1-3 meses (efectivo)",
}

ASSET_CLASSES = ["Acciones EE.UU.", "Acciones internacionales", "Renta fija", "Activos reales", "Efectivo"]
CASH = "BIL"
START = "2007-12-01"   # el primer retorno mensual es enero de 2008
END = "2026-11-01"     # fecha exclusiva: el último precio es de octubre de 2026


def download_prices(tickers=None, start=START, end=END):
    """Precios diarios de cierre ajustados (dividendos y splits)."""
    import yfinance as yf
    tickers = list(tickers or UNIVERSE)
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
    missing = [t for t in tickers if t not in prices.columns]
    if missing:
        raise RuntimeError(f"yfinance no devolvió datos para: {missing}")
    return prices[tickers].sort_index()


def monthly_returns(prices):
    """Retornos simples mensuales a partir del último precio de cada mes."""
    try:
        month_end = prices.resample("ME").last()
    except ValueError:          # pandas < 2.2
        month_end = prices.resample("M").last()
    rets = month_end.pct_change(fill_method=None).iloc[1:]
    return rets.dropna(how="any")


def save_returns(rets, path="data/monthly_returns.csv"):
    rets.to_csv(path, index_label="date")


def load_returns(path="data/monthly_returns.csv"):
    rets = pd.read_csv(path, index_col=0, parse_dates=True)
    return rets[[t for t in UNIVERSE if t in rets.columns]]
