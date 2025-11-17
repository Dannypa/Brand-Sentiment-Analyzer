import praw
import pandas as pd
from datetime import datetime
from typing import List
from models import PostCache
from db import search_post_database, insert_post_cache
import datetime as dt
from .ml_client import get_sentiment
import numpy as np
import time


def init_reddit(client_id, client_secret, user_agent):
    """Initialize Reddit client"""
    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

def fetch_top_posts(reddit_client, subreddits: list[str], time_filter="month", limit=100):
    """Fetch top posts and comments from subreddits (no keyword restriction)"""
    posts, comments = [], []
    
    for sub in subreddits:
        subreddit = reddit_client.subreddit(sub)
        for post in subreddit.top(time_filter=time_filter, limit=limit):
            posts.append({
                "subreddit": sub,
                "id": post.id,
                "title": post.title,
                "content": post.selftext,
                "created_utc": post.created_utc,
                "score": post.score,
                "num_comments": post.num_comments
            })
            
            post.comments.replace_more(limit=0)
            for comment in post.comments.list():
                comments.append({
                    "subreddit": sub,
                    "post_id": post.id,
                    "content": comment.body,
                    "created_utc": comment.created_utc,
                    "score": comment.score
                })
    
    return pd.DataFrame(posts), pd.DataFrame(comments)

def fetch_keyword_search(reddit_client, subreddits: list[str], keywords: list[str], 
                         time_filter="year", limit_per_sub=50):
    """Fetch posts and comments based on keyword search"""
    all_data = []
    
    for subreddit_name in subreddits:
        subreddit = reddit_client.subreddit(subreddit_name)
        
        for keyword in keywords:
            search_results = subreddit.search(keyword, time_filter=time_filter, limit=limit_per_sub)
            
            for submission in search_results:
                all_data.append({
                    'type': 'post',
                    'id': submission.id,
                    'title': submission.title,
                    'content': submission.selftext,
                    'score': submission.score,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'subreddit': subreddit_name,
                    'keyword': keyword
                })
                
                submission.comments.replace_more(limit=5)
                for comment in submission.comments.list()[:20]:
                    all_data.append({
                        'type': 'comment',
                        'id': comment.id,
                        'post_id': submission.id,
                        'content': comment.body,
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'subreddit': subreddit_name,
                        'keyword': keyword
                    })
    
    return pd.DataFrame(all_data)


def get_all_post_data(conn, reddit, brand, limit_per_sub, cutoff = None) -> List[PostCache]:
    # start = time.perf_counter()
    try:
        post_data = search_post_database(conn, brand, datetime.now() - dt.timedelta(days=30), datetime.now())
    except Exception as e:
        print("Error searching database for %s: %s" % (brand, e))
        post_data = []
    # print("Found %d cached posts for brand %s" % (len(post_data), brand))

    if len(post_data) < limit_per_sub:
        try:
            posts_df, comments_df = fetch_top_posts(reddit, [brand], time_filter="month", limit=limit_per_sub) # limit=limit_per_sub+50 if want to get more posts
        except Exception as e:
            print("Error fetching reddit data for %s: %s" % (brand, e))
            posts_df = pd.DataFrame()
            comments_df = pd.DataFrame()

        # If there are no posts returned, bail out
        if posts_df is None or posts_df.empty:
            # elapsed = time.perf_counter() - start
            # print("get_all_post_data for %s returned %d posts in %.3fs (no new posts)" % (brand, len(post_data), elapsed))
            return post_data

        # Iterate over fetched posts and attach comment sentiments
        for _, row in posts_df.iterrows():
            date = datetime.fromtimestamp(row.get("created_utc"))
            # if cutoff is None or date > cutoff:
            #     continue
            comments_for_post = comments_df[comments_df["post_id"] == row["id"]] if not comments_df.empty else pd.DataFrame()
            title = (str(row.get("title", "")) + " " + str(row.get("content", ""))).strip()
            title_sentiment = get_sentiment([title])[0]
            comment_texts = comments_for_post["content"].tolist() if not comments_for_post.empty else []
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
                print("Error inserting PostCache into database for post_id %s: %s" % (row['id'], e))
                continue
    # elapsed = time.perf_counter() - start
    # print("get_all_post_data for %s returned %d posts in %.3fs" % (brand, len(post_data), elapsed))
    return post_data