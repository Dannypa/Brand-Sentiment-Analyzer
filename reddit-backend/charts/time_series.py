# reddit-backend/charts/time_series.py
"""
Build a time-series of average sentiment over time using keyword search (NOT top-posts).
This uses the keyword-search method from reddit_unified.reddit_access.
"""

from typing import List, Optional
import os
import math
import requests
import pandas as pd
import plotly.express as px
from pydantic import JsonValue
from datetime import datetime, timezone

from .data_access import init_reddit, fetch_keyword_search  # adjust import to your layout

ML_URL = os.environ.get("ML_URL", "http://ml:8080").rstrip("/")

def _chunk_list(xs: List, chunk_size: int):
    for i in range(0, len(xs), chunk_size):
        yield xs[i:i+chunk_size]

def _make_teams_from_keyword_df(df: pd.DataFrame, brand: str):
    """
    The keyword search function returns mixed rows (posts and comments).
    Each row becomes its own team with texts=[content] to get an item-level sentiment.
    We keep some metadata for mapping.
    Returns (teams_list, metadata_rows) where metadata_rows is a list of dicts aligning with teams_list order.
    """
    teams = []
    meta = []
    if df.empty:
        return teams, meta

    # prefer 'content' column; fallback to 'title' or others
    for _, row in df.iterrows():
        content = ""
        if "content" in row and pd.notna(row["content"]):
            content = str(row["content"])
        elif "title" in row and pd.notna(row["title"]):
            content = str(row["title"])
        else:
            continue
        teams.append({"brand": brand, "title": row.get("title", row.get("id")), "texts": [content]})
        meta.append({
            "id": row.get("id"),
            "date": None if pd.isna(row.get("created_utc")) else pd.to_datetime(float(row.get("created_utc")), unit='s').date(),
            "subreddit": row.get("subreddit"),
            "type": row.get("type", "post")
        })
    return teams, meta

def time_series_sentiment(brand: str, subreddits: Optional[List[str]] = None, keywords: Optional[List[str]] = None, time_filter: str = "year", fetch_limit: int = 200, ml_batch_size: int = 100, group_by: str = "date") -> JsonValue:
    """
    Build a daily average sentiment time-series for content matching keywords.
    - brand: used as the default keyword if keywords=None
    - subreddits: list of subreddits in which to search (required)
    """

    if subreddits is None:
        raise ValueError("time_series_sentiment requires 'subreddits' argument (list of subreddit names).")

    # keywords: use brand if not provided
    if not keywords:
        keywords = [brand]

    reddit = init_reddit(None, None, None)
    df = fetch_keyword_search(reddit, subreddits, keywords, time_filter=time_filter, limit_per_sub=fetch_limit)
    if df.empty:
        # return an empty time-series (simple zero-length figure)
        fig = px.line(x=[], y=[])
        return fig.to_json()

    teams, meta = _make_teams_from_keyword_df(df, brand)
    if not teams:
        fig = px.line(x=[], y=[])
        return fig.to_json()

    # call ML in batches
    all_scores = []
    for batch in _chunk_list(teams, ml_batch_size):
        r = requests.post(f"{ML_URL}/get_sentiment", json={"teams": batch}, timeout=30)
        r.raise_for_status()
        resp_json = r.json()
        sentiments = resp_json.get("sentiment", resp_json if isinstance(resp_json, list) else [])
        # each inner sentiment list contains one float (because each team has one text in this design)
        for inner in sentiments:
            if inner:
                all_scores.append(float(inner[0]))
            else:
                all_scores.append(0.0)

    # map back to meta (teams order == meta order)
    # build DataFrame with date and sentiment
    rows = []
    for m, score in zip(meta, all_scores):
        rows.append({"date": m["date"], "subreddit": m.get("subreddit", "all"), "sentiment": score})

    df_plot = pd.DataFrame(rows)
    # drop missing dates
    df_plot = df_plot.dropna(subset=["date"])
    if df_plot.empty:
        fig = px.line(x=[], y=[])
        return fig.to_json()

    # group by date and subreddit (or group_by)
    if group_by == "date":
        grouped = df_plot.groupby("date")["sentiment"].mean().reset_index()
        fig = px.line(grouped, x="date", y="sentiment", title=f"Daily average sentiment for '{brand}'")
    else:
        grouped = df_plot.groupby(["subreddit", "date"])["sentiment"].mean().reset_index()
        fig = px.line(grouped, x="date", y="sentiment", color="subreddit", title=f"Daily average sentiment for '{brand}'")
    fig.update_layout(yaxis_title="Avg sentiment (-1 to 1)", template="plotly_white")
    return fig.to_json()