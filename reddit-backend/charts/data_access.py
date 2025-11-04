import praw
from datetime import datetime
import pandas as pd
import os
from typing import List, Optional, Tuple

# what does this mean? should I hardcode my api shit in?
def init_reddit(client_id: Optional[str] = None,
                client_secret: Optional[str] = None,
                user_agent: Optional[str] = None,
                request_timeout: int = 10):
    """Create a PRAW Reddit client. Reads from environment by default.

    Adds a request timeout to avoid blocking indefinitely when Reddit is slow.
    """
    # Prefer explicit args, fall back to environment variables.
    client_id = client_id or os.environ.get("REDDIT_CLIENT_ID")
    client_secret = client_secret or os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = user_agent or os.environ.get("REDDIT_USER_AGENT")

    if not client_id or not client_secret:
        raise ValueError("Reddit client_id / client_secret not set in env or arguments")

    # requestor_kwargs sets the underlying requests timeout for HTTP calls
    requestor_kwargs = {"timeout": request_timeout}
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        requestor_kwargs=requestor_kwargs
    )
def fetch_top_posts(reddit_client, subreddits: List[str], time_filter: str = "month", limit: int = 100) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fetch top posts and flattened comments for a list of subreddits.

    Returns (posts_df, comments_df). On error returns empty DataFrames with expected columns.
    """
    posts = []
    comments = []

    try:
        for sub in subreddits:
            subreddit = reddit_client.subreddit(sub)
            for post in subreddit.top(time_filter=time_filter, limit=limit):
                posts.append({
                    "subreddit": sub,
                    "id": post.id,
                    "title": post.title,
                    "content": getattr(post, "selftext", "") or "",
                    "created_utc": post.created_utc,
                    "score": post.score,
                    "num_comments": post.num_comments,
                })

                # Expand and collect comments (safely avoid "more" objects)
                post.comments.replace_more(limit=0)
                for comment in post.comments.list():
                    try:
                        body = comment.body
                    except Exception:
                        continue
                    comments.append({
                        "subreddit": sub,
                        "post_id": post.id,
                        "content": body,
                        "created_utc": comment.created_utc,
                        "score": getattr(comment, "score", 0),
                    })
    except Exception as e:
        print(f"[error] fetch_top_posts failed: {e}")
        # return empty dataframes with expected columns to keep downstream code stable
        posts_df = pd.DataFrame(columns=["subreddit", "id", "title", "content", "created_utc", "score", "num_comments"])
        comments_df = pd.DataFrame(columns=["subreddit", "post_id", "content", "created_utc", "score"])
        return posts_df, comments_df

    posts_df = pd.DataFrame(posts)
    comments_df = pd.DataFrame(comments)

    # normalize empty frames to have expected columns
    if posts_df.empty:
        posts_df = pd.DataFrame(columns=["subreddit", "id", "title", "content", "created_utc", "score", "num_comments"])
    if comments_df.empty:
        comments_df = pd.DataFrame(columns=["subreddit", "post_id", "content", "created_utc", "score"])

    return posts_df, comments_df

def fetch_keyword_search(reddit_client, subreddits: list[str], keywords: list[str], time_filter: str = "year", limit_per_sub: int = 50) -> pd.DataFrame:
    all_data = []

    for subreddit_name in subreddits:
        subreddit = reddit_client.subreddit(subreddit_name)

        for keyword in keywords:
            search_results = subreddit.search(keyword, time_filter=time_filter, limit=limit_per_sub)

            for submission in search_results:
                all_data.append({
                    "type": "post",
                    "id": submission.id,
                    "title": submission.title,
                    "content": getattr(submission, "selftext", "") or "",
                    "score": submission.score,
                    "num_comments": submission.num_comments,
                    "created_utc": submission.created_utc,
                    "subreddit": subreddit_name,
                    "keyword": keyword,
                })

                submission.comments.replace_more(limit=5)
                for comment in submission.comments.list()[:20]:

                        all_data.append({
                            "type": "comment",
                            "id": comment.id,
                            "post_id": submission.id,
                            "content": getattr(comment, "body", ""),
                            "score": getattr(comment, "score", 0),
                            "created_utc": getattr(comment, "created_utc", None),
                            "subreddit": subreddit_name,
                            "keyword": keyword,
                        })

    return pd.DataFrame(all_data)