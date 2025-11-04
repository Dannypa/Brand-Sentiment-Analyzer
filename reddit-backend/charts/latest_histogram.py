"""
Generate a histogram of per-post average sentiment for "top posts" in given subreddit(s).
"""
# how are brands and subreddits different?
from typing import List, Optional
import os
import math
import json
import requests
import pandas as pd
import plotly.express as px
from pydantic import JsonValue

from .data_access import init_reddit, fetch_top_posts  

# ML url default
ML_URL = os.environ.get("ML_URL", "http://ml:8080").rstrip("/")


def _chunk_list(xs: List, chunk_size: int):
    for i in range(0, len(xs), chunk_size):
        yield xs[i:i+chunk_size]

def _build_teams_from_posts(posts_df: pd.DataFrame, comments_df: pd.DataFrame, brand: str, top_n_comments: int = 10):
    """
    Build a list of team dicts: one team per post.
    texts: [title, content, top_comment1, top_comment2 ...]
    """
    teams = []
    if posts_df.empty:
        return teams

    # ensure comments_df has post_id column
    if not comments_df.empty:
        comments_df = comments_df.rename(columns={"post_id": "id"}) if "post_id" in comments_df.columns else comments_df

    for _, row in posts_df.iterrows():
        post_id = row.get("id")
        title = row.get("title", "") or ""
        content = row.get("content", "") or ""
        
        # get comments for this post (robust selection)
        post_comments = pd.DataFrame()
        if not comments_df.empty:
            # Prefer 'post_id' (common). Coerce to string for robust comparison.
            if "post_id" in comments_df.columns:
                post_comments = comments_df[comments_df["post_id"].astype(str) == str(post_id)]
            elif "id" in comments_df.columns:
                # Some comment frames may include the related id under 'id' (less common).
                post_comments = comments_df[comments_df["id"].astype(str) == str(post_id)]
            else:
                # Try some other possible column names that might reference the parent post
                for col in ["parent_id", "reply_to", "postid", "post_id_str"]:
                    if col in comments_df.columns:
                        post_comments = comments_df[comments_df[col].astype(str) == str(post_id)]
                        break
        else:
            post_comments = pd.DataFrame()

        # sort by score if present
        if not post_comments.empty and "score" in post_comments.columns:
            post_comments = post_comments.sort_values("score", ascending=False)

        # extract comment text(s), prefer 'content' then 'body'
        comment_texts = []
        if not post_comments.empty:
            if "content" in post_comments.columns:
                comment_texts = post_comments["content"].astype(str).tolist()[:top_n_comments]
            elif "body" in post_comments.columns:
                comment_texts = post_comments["body"].astype(str).tolist()[:top_n_comments]
       
        texts = [t for t in [title, content] + comment_texts if t and str(t).strip()]
        if not texts:
            continue
        teams.append({"brand": brand, "title": title or post_id, "texts": texts})
    return teams

def histogram_sentiment(brand: str, subreddits: Optional[List[str]] = None, time_filter: str = "month", fetch_limit: int = 100, top_n_comments: int = 10, ml_batch_size: int = 50) -> JsonValue:
    """
    Parameters:
    - brand: input string (interpreted as a subreddit name or a comma-separated list of subreddits).
    - subreddits: optional explicit list of subreddit names to query. If None, brand is split on commas.
    - time_filter: e.g., "month"
    - fetch_limit: how many top posts to fetch per subreddit
    - top_n_comments: how many comments per post to include
    - ml_batch_size: how many teams to POST per ML request
    """
    # interpret brand as substring for default subreddits (split by comma)
    if subreddits is None:
        sub_list = [s.strip() for s in brand.split(",") if s.strip()]
    else:
        sub_list = subreddits
      
    # init reddit client
    reddit = init_reddit(None, None, None)

    # fetch top posts + comments
    posts_df, comments_df = fetch_top_posts(reddit, sub_list, time_filter=time_filter, limit=fetch_limit)

    # build teams
    teams = _build_teams_from_posts(posts_df, comments_df, brand, top_n_comments=top_n_comments)
    if not teams:
        # return empty histogram (an empty figure) to avoid error in UI
        fig = px.histogram(x=[])
        return fig.to_json()

    # call ML in batches
    all_sentiments = []
    for batch in _chunk_list(teams, ml_batch_size):
        req = {"teams": batch}
        r = requests.post(f"{ML_URL}/get_sentiment", json=req, timeout=15)
        r.raise_for_status()
        resp_json = r.json()
        # resp_json expected to be {"sentiment": [ [...], [...], ... ]} OR the ml service in repo returns SentimentResponse model.
        sentiments = resp_json.get("sentiment", resp_json if isinstance(resp_json, list) else [])
        # ensure we flatten/extend in same order
        all_sentiments.extend(sentiments)

    # compute per-team average sentiment
    avg_sentiments = []
    for s in all_sentiments:
        if not s:
            avg = 0.0
        else:
            # numeric values; guard
            nums = [float(x) for x in s]
            avg = sum(nums) / len(nums)
        avg_sentiments.append(avg)

    # build DataFrame mapping back to posts
    df_plot = pd.DataFrame({"avg_sentiment": avg_sentiments})
    fig = px.histogram(df_plot, x="avg_sentiment", nbins=20, title=f"Sentiment distribution (top posts) for {', '.join(sub_list)}")
    fig.update_layout(xaxis_title="Avg sentiment (-1 to 1)", yaxis_title="Count", template="plotly_white")

    # Sanitize Plotly figure dict for JSON (replace NaN/Inf with null) and return
    fig.to_JSON()
 #   fig_dict = fig.to_dict()
  #  safe = _sanitize_for_json(fig_dict)
   # return json.dumps(safe, ensure_ascii=False)

