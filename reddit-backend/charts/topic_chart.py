# reddit-backend/charts/topic_chart.py
"""
Topic-based chart: proportion of NEG/NEU/POS for a given topic/keyword.
Uses the keyword search method (recommended for topic-level queries).
"""

from typing import List, Optional
import os
import requests
import pandas as pd
import plotly.express as px
from pydantic import JsonValue

from .data_access import init_reddit, fetch_keyword_search  # adjust import to actual path

ML_URL = os.environ.get("ML_URL", "http://ml:8080").rstrip("/")

def _chunk_list(xs: List, chunk_size: int):
    for i in range(0, len(xs), chunk_size):
        yield xs[i:i+chunk_size]

def _category_from_score(s: float) -> str:
    if s <= -0.05:
        return "NEG"
    if s >= 0.05:
        return "POS"
    return "NEU"

def topic_chart(topic: str, subreddits: Optional[List[str]] = None, time_filter: str = "year", fetch_limit: int = 200, ml_batch_size: int = 100) -> JsonValue:
    if not subreddits:
        raise ValueError("topic_chart requires a list of subreddits to search in.")

    reddit = init_reddit(None, None, None)
    df = fetch_keyword_search(reddit, subreddits, [topic], time_filter=time_filter, limit_per_sub=fetch_limit)
    if df.empty:
        fig = px.pie(values=[], names=[], title=f"No data for topic '{topic}'")
        return fig.to_json()

    # Build teams: one team per row (post or comment) with a single text
    teams = []
    meta = []
    for _, row in df.iterrows():
        content = row.get("content") or row.get("title") or ""
        if not content or str(content).strip() == "":
            continue
        teams.append({"brand": topic, "title": row.get("title", row.get("id")), "texts": [str(content)]})
        meta.append({"subreddit": row.get("subreddit"), "id": row.get("id")})

    if not teams:
        fig = px.pie(values=[], names=[], title=f"No textual data for topic '{topic}'")
        return fig.to_json()

    all_scores = []
    for batch in _chunk_list(teams, ml_batch_size):
        r = requests.post(f"{ML_URL}/get_sentiment", json={"teams": batch}, timeout=30)
        r.raise_for_status()
        resp_json = r.json()
        sentiments = resp_json.get("sentiment", resp_json if isinstance(resp_json, list) else [])
        for inner in sentiments:
            if inner:
                all_scores.append(float(inner[0]))
            else:
                all_scores.append(0.0)

    # transform into categories
    cats = [_category_from_score(s) for s in all_scores]
    counts = pd.Series(cats).value_counts().reindex(["NEG", "NEU", "POS"]).fillna(0).astype(int)
    chart_df = pd.DataFrame({"sentiment": counts.index.tolist(), "count": counts.values.tolist()})
    fig = px.pie(chart_df, values="count", names="sentiment", title=f"Sentiment distribution for topic '{topic}' (NEG/NEU/POS)", hole=0.4)
    fig.update_traces(textposition='outside', textinfo='percent+label')
    fig.update_layout(template="plotly_white")
    return fig.to_json()