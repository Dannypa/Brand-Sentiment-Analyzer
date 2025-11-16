import os
import pandas as pd
import plotly.express as px
import plotly.io as pio
from datetime import datetime, timedelta, timezone
from typing import List
import numpy as np
from models import PostCache

from .reddit_access import init_reddit, fetch_keyword_search, get_all_post_data
from .ml_client import get_sentiment


def time_series_sentiment(conn, brands: List[str], days: int = 30) -> str:
    """Daily average sentiment time series for each brand from Reddit.

    brands: list of brand keywords.
    days: lookback window in days.
    """
    client_id = os.environ.get("REDDIT_APP_ID")
    client_secret = os.environ.get("REDDIT_APP_SECRET")
    user_agent = os.environ.get("REDDIT_APP_NAME")

    if not client_id or not client_secret:
        fig = px.line(title="Reddit credentials not configured")
        fig.update_layout(template="plotly_white")
        return pio.to_json(fig)

    reddit = init_reddit(client_id, client_secret, user_agent)

    all_rows = []
    cutoff = datetime.now() - timedelta(days=days)

    for brand in brands:
        post_data = get_all_post_data(conn, reddit, brand, 100, cutoff)
        sentiments = [post.avg_sentiment for post in post_data if post.avg_sentiment is not None]
        dates = [post.datetime.date() for post in post_data if post.avg_sentiment is not None]
        for d, s in zip(dates, sentiments if sentiments else [0.0] * len(dates)):
            all_rows.append({"date": d, "brand": brand, "sentiment": s})

    if not all_rows:
        fig = px.line(title="No data available")
        fig.update_layout(template="plotly_white")
        return pio.to_json(fig)

    df_all = pd.DataFrame(all_rows)
    daily = df_all.groupby(["brand", "date"])['sentiment'].mean().reset_index()

    fig = px.line(daily, x="date", y="sentiment", color="brand", markers=True, title="Daily Average Sentiment")
    fig.update_layout(template="plotly_white", yaxis_title="Average Sentiment (-1 to 1)")
    return pio.to_json(fig)