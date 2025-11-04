import os
import plotly.express as px
from pydantic import JsonValue
from typing import List, Optional

from .reddit_access import init_reddit, fetch_keyword_search
from .ml_client import get_sentiment


def topic_chart(topic: str, brands: List[str]) -> JsonValue:
    """Return a histogram JSON for sentiment of a topic across multiple brands.

    For each brand, the function searches Reddit for `topic` + `brand` and
    aggregates sentiment of matching posts/comments.
    """
    client_id = os.environ.get("REDDIT_APP_ID")
    client_secret = os.environ.get("REDDIT_APP_SECRET")
    user_agent = os.environ.get("REDDIT_APP_NAME")

    if not client_id or not client_secret:
        fig = px.histogram(title="Reddit credentials not configured")
        fig.update_layout(template="plotly_white")
        return fig.to_json()

    reddit = init_reddit(client_id, client_secret, user_agent)

    rows = []
    for brand in brands:
        keyword = f"{topic} {brand}"
        try:
            df = fetch_keyword_search(reddit, ["all"], [keyword], time_filter="year", limit_per_sub=50)
        except Exception as e:
            print(f"Error fetching reddit data for {keyword}: {e}")
            df = pd.DataFrame()

        texts = []
        if df is None or df.empty:
            texts = []
        else:
            for _, row in df.iterrows():
                if row.get("type") == "post":
                    t = (str(row.get("title", "")) + " " + str(row.get("content", ""))).strip()
                else:
                    t = row.get("content") or row.get("body") or ""
                if t:
                    texts.append(t)

        sentiments = get_sentiment(texts) if texts else []
        for s in sentiments if sentiments else [0.0]:
            rows.append({"brand": brand, "sentiment": s})

    if not rows:
        fig = px.histogram(x=[0.0], nbins=10, title=f"Sentiment distribution for {topic}")
        fig.update_layout(template="plotly_white")
        return fig.to_json()

    import pandas as pd

    df_all = pd.DataFrame(rows)
    fig = px.histogram(df_all, x="sentiment", color="brand", barmode="overlay", nbins=20, title=f"Sentiment distribution for {topic}")
    fig.update_layout(template="plotly_white")
    return fig.to_json()