"""
Bridge between the copied quant core and the API: calls the engine, makes the
result JSON-safe (DataFrames -> records, NaN -> null), and caches each result in
Redis so all users share one upstream fetch per cache window (rate-limit safety).
"""
import datetime
import math

import numpy as np
import pandas as pd
from django.conf import settings
from django.core.cache import cache

import gex_core
import chain_core
import macro_core
import fundamentals_core

TTL = getattr(settings, "MARKET_CACHE_TTL", 90)


def json_safe(o):
    if isinstance(o, dict):
        return {str(k): json_safe(v) for k, v in o.items()}
    if isinstance(o, (list, tuple, set)):
        return [json_safe(v) for v in o]
    if isinstance(o, pd.DataFrame):
        df = o.copy()
        df = df.reset_index()
        df.columns = [str(c) for c in df.columns]
        return [json_safe(rec) for rec in df.to_dict(orient="records")]
    if isinstance(o, pd.Series):
        return {str(k): json_safe(v) for k, v in o.to_dict().items()}
    if isinstance(o, pd.Timestamp):
        return o.isoformat()
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        f = float(o)
        return None if math.isnan(f) else f
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, float):
        return None if math.isnan(o) else o
    return o


def _cached(key, fn):
    val = cache.get(key)
    if val is None:
        val = json_safe(fn())
        cache.set(key, val, TTL)
    return val


# ── GEX ───────────────────────────────────────────────────────────────────────
def gex_all():
    return _cached("gex:all", gex_core.compute_all)


def gex_symbol(sym):
    return _cached(f"gex:{sym}", lambda: gex_core.compute_symbol(sym))


# ── Exposure (DEX / GEX / VEX / VEGA / CHARM) ────────────────────────────────
def exposure(sym, greek):
    def _fn():
        r = chain_core.load_chain(sym)
        if r.get("error"):
            return r
        agg = chain_core.aggregate_greek(r["df"], r["spot"], greek)
        return {"symbol": sym, "greek": greek, "spot": r["spot"], "agg": agg}
    return _cached(f"exp:{sym}:{greek}", _fn)


# ── Chain / OI / vol ─────────────────────────────────────────────────────────
def chain(sym):
    return _cached(f"chain:{sym}", lambda: chain_core.load_chain(sym, strike_range=0.20))


# ── Macro ────────────────────────────────────────────────────────────────────
def macro_nq():
    return _cached("macro:nq", macro_core.compute_nq_bias)


def macro_events():
    return _cached("macro:events", macro_core.event_risk)


# ── Fundamentals ─────────────────────────────────────────────────────────────
def fundamentals(sym, discount=None):
    key = f"fund:{sym}:{discount}"
    return _cached(key, lambda: fundamentals_core.analyze(sym, discount_override=discount))


# ── Price candles (for the TradingView chart) ────────────────────────────────
_YF_FUT = {"ES": "ES=F", "NQ": "NQ=F", "GC": "GC=F"}


def price(sym, interval="15m", period="5d"):
    yf_sym = _YF_FUT.get(sym, sym)

    def _fn():
        import yfinance as yf
        try:
            h = yf.Ticker(yf_sym).history(period=period, interval=interval)
        except Exception as exc:
            return {"symbol": sym, "candles": [], "error": str(exc)}
        if h is None or h.empty:
            return {"symbol": sym, "candles": []}
        candles = []
        for ts, row in h.iterrows():
            try:
                candles.append({
                    "time": int(ts.timestamp()),
                    "open": float(row["Open"]), "high": float(row["High"]),
                    "low": float(row["Low"]), "close": float(row["Close"]),
                })
            except Exception:
                continue
        return {"symbol": sym, "candles": candles}
    return _cached(f"price:{sym}:{interval}:{period}", _fn)
