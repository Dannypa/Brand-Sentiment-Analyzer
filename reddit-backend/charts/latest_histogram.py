import os
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.io as pio
import numpy as np
from typing import List
import psycopg2
from models import PostCache
from datetime import datetime
import datetime as dt
from db import search_post_database, insert_post_cache

from .reddit_access import init_reddit, fetch_keyword_search, get_all_post_data
from .ml_client import get_sentiment


def histogram_sentiment(conn, brands: List[str]) -> str:
    """
    Create a sentiment histogram for given brands from Reddit data.

    Last month posts. Search the "r/all" subreddit for each brand as a keyword then compute sentiment.
    TODO: change to fetch_top_posts to get last month top posts (from corresponding subreddits), but this would require having a list of brands before hand and implementing some sort of brand search in the search box of the front end.
    """
    client_id = os.environ.get("REDDIT_APP_ID")
    client_secret = os.environ.get("REDDIT_APP_SECRET")
    user_agent = os.environ.get("REDDIT_APP_NAME")

    if not client_id or not client_secret:
        # Return an empty chart with message if creds missing
        fig = go.Figure()
        fig.update_layout(title="Reddit credentials not configured", template="plotly_white")
        return pio.to_json(fig)

    reddit = init_reddit(client_id, client_secret, user_agent)

    hist_data = []
    group_labels = []

    for brand in brands:
        print(f"Processing brand: {brand}")
        post_data = get_all_post_data(conn, reddit, brand, 50)
        print(f"Fetched {len(post_data)} posts for brand {brand}")
        sentiments = [post.avg_sentiment for post in post_data if post.avg_sentiment is not None]
        print(sentiments)
        hist_data.append(sentiments)
        group_labels.append(brand)


    # If nothing to plot, return empty figure
    if not hist_data or not group_labels:
        fig = go.Figure()
        fig.update_layout(title="No data available", template="plotly_white")
        return pio.to_json(fig)

    try:
        fig = ff.create_distplot(hist_data, group_labels, curve_type="kde", bin_size=0.1, show_rug=False)
    except Exception as e:
        print(f"Error creating distplot: {e}")
        fig = go.Figure()
        fig.update_layout(title="No data available", template="plotly_white")
        return pio.to_json(fig)

    fig.update_layout(title="Sentiment Distribution (estimated)", xaxis_title="Sentiment (-1 to 1)", yaxis_title="Number of items")
    fig.update_layout(template="plotly_white")
    return pio.to_json(fig)
