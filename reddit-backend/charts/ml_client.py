"""Central ML client helper for calling the project's sentiment API.

Provides a single exported function `get_sentiment(texts: list[str]) -> list[float]`.
"""
from __future__ import annotations

import os
import requests
from typing import List


ML_URL = os.environ.get("ML_URL", "http://ml:8080/get_sentiment")


def get_sentiment(texts: List[str]) -> List[float]:
    """Call the ML service and return a flat list of sentiment floats.

    The ML endpoint is expected to accept payload: {"teams": [{"texts": texts}]}
    and return JSON with a `sentiment` key. The function is defensive and will
    normalize nested lists like [[...]] to a single flat list. On error it
    returns an empty list.
    """
    if not texts:
        return []

    try:
        payload = {"teams": [{"texts": texts}]}
        resp = requests.post(ML_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        sentiment = data.get("sentiment")
        if sentiment is None:
            return []

        # Normalize double-nested lists (e.g., [[...]] -> [...])
        if isinstance(sentiment, list) and len(sentiment) > 0 and isinstance(sentiment[0], list):
            sentiment = sentiment[0]

        return list(sentiment)
    except Exception:
        # Swallow exceptions here and return empty list; callers should handle fallbacks.
        return []
