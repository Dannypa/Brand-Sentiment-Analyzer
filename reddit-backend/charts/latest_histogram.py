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

from .reddit_access import init_reddit, fetch_keyword_search
from .ml_client import get_sentiment


def histogram_sentiment(brands: List[str], conn) -> str:
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

def get_all_post_data(conn, reddit, brand, limit_per_sub) -> List[PostCache]:
    
    try:
        post_data = search_post_database(conn, brand, datetime.now() - dt.timedelta(days=30), datetime.now())
    except Exception as e:
        print(f"Error searching database for {brand}, {e}")
        post_data = []
    print(f"Found {len(post_data)} cached posts for brand {brand}")

    if len(post_data) < limit_per_sub:
        try:
            df = fetch_keyword_search(reddit, ["all"], [brand], time_filter="month", limit_per_sub=limit_per_sub+50)
        except Exception as e:
            print(f"Error fetching reddit data for {brand}: {e}")
            df = pd.DataFrame()

        if df is None or df.empty:
            return post_data
        else:
            posts_df = df[df["type"] == "post"]
            comments_df = df[df["type"] == "comment"]
            # fetch_keyword_search returns rows for posts and comments
            for _, row in posts_df.iterrows():
                comments_for_post = comments_df[comments_df["post_id"] == row["id"]]
                title = (str(row.get("title", "")) + " " + str(row.get("content", ""))).strip()
                title_sentiment = get_sentiment([title])[0]
                comment_texts = comments_for_post["content"].tolist()
                comment_sentiments = get_sentiment(comment_texts)
                avg_comment_sentiment = np.mean(comment_sentiments) if comment_sentiments else 0.0
                combined_sentiment = np.mean([title_sentiment, avg_comment_sentiment])
                try:
                    post_cache = PostCache(
                        post_id=row["id"],
                        query=brand,
                        subreddit=row.get("subreddit", "all"),
                        datetime=datetime.fromtimestamp(row.get("created_utc")),
                        title_sentiment=title_sentiment,
                        avg_comment_sentiment=avg_comment_sentiment,
                        avg_sentiment=combined_sentiment
                    )
                except Exception as e:
                    print(f"Error creating PostCache for post_id {row['id']}: {e}")
                    continue
                post_data.append(post_cache)
                try:
                    insert_post_cache(conn, post_cache)
                except Exception as e:
                    print(f"Error inserting PostCache into database for post_id {row['id']}: {e}")
                    continue
    return post_data