"""
API Integration: Live Foreign Exchange Rate Lookup
==========================================================================
Satisfies REQ-02 (standardise all transaction amounts to GBP).

Uses the Frankfurter API (https://www.frankfurter.app) — a free,
no-authentication exchange rate API backed by the European Central Bank.
In a production banking environment, this would call the bank's licensed
FX data provider instead, but the integration pattern (request, validate,
cache, handle failure) is the same regardless of provider.

Demonstrates: requests library usage, error handling, retry logic,
and writing a reusable function rather than one-off script code.
"""

import requests
import json
import time
from datetime import date

FX_API_BASE = "https://api.frankfurter.app"
TARGET_CURRENCY = "GBP"
SUPPORTED_CURRENCIES = ["EUR", "USD", "GBP"]


def get_exchange_rates(base_date: str = None, retries: int = 3, backoff: float = 1.5) -> dict:
    """
    Fetch exchange rates to GBP for a given date (defaults to latest).

    Returns a dict like {"EUR": 0.86, "USD": 0.79, "GBP": 1.0}

    Includes retry logic with exponential backoff — a real integration
    can't assume the first call always succeeds.
    """
    endpoint = f"{FX_API_BASE}/latest" if base_date is None else f"{FX_API_BASE}/{base_date}"
    params = {"to": ",".join(c for c in SUPPORTED_CURRENCIES if c != TARGET_CURRENCY)}

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            rates = data.get("rates", {})
            rates[TARGET_CURRENCY] = 1.0  # GBP to GBP is always 1
            return rates

        except requests.exceptions.RequestException as e:
            print(f"[Attempt {attempt}/{retries}] FX API request failed: {e}")
            if attempt < retries:
                time.sleep(backoff ** attempt)
            else:
                print("FX API unreachable after retries. Falling back to cached rates.")
                return _load_fallback_rates()


def _load_fallback_rates() -> dict:
    """
    Fallback rates used if the live API is unreachable (e.g. no network,
    provider outage). In production this would read the last successfully
    cached rate set rather than hardcoded values — flagged here for
    transparency since this sandbox has restricted outbound network access.
    """
    print("Using fallback rate cache (last known good rates).")
    return {"GBP": 1.0, "EUR": 0.86, "USD": 0.79}


def convert_to_gbp(amount: float, currency: str, rates: dict) -> float:
    """Convert a single transaction amount to GBP using a rates dict."""
    if currency not in rates or currency is None:
        return None  # flagged downstream by the data quality framework
    rate = rates[currency]
    return round(amount * rate, 2)


if __name__ == "__main__":
    print("Fetching live exchange rates to GBP...")
    rates = get_exchange_rates()
    print("Rates retrieved:", rates)

    with open("../data/exchange_rates.json", "w") as f:
        json.dump({"as_of": str(date.today()), "rates": rates}, f, indent=2)

    print("Saved to ../data/exchange_rates.json")

    # quick sanity check
    print("\nSample conversions:")
    for amt, cur in [(100, "EUR"), (50, "USD"), (75, "GBP")]:
        print(f"  {amt} {cur} -> £{convert_to_gbp(amt, cur, rates)}")
