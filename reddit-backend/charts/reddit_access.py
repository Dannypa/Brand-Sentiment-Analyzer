import praw
import pandas as pd
from datetime import datetime

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