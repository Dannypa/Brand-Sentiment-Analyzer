# test_latest_histogram_local.py
# Run this from inside the reddit-backend folder.
import pandas as pd
import os
import requests
import json
import plotly.express as px

# Import the local builder function (adjust if your module layout differs)
from charts.latest_histogram import _build_teams_from_posts

# Synthetic posts + comments (same schema expected by _build_teams_from_posts)
posts = [
    {"subreddit": "testsub", "id": "p1", "title": "Great product", "content": "I love using this every day", "created_utc": 1690000000, "score": 10, "num_comments": 2},
    {"subreddit": "testsub", "id": "p2", "title": "Bad quality", "content": "Broke after a week", "created_utc": 1690001000, "score": 2, "num_comments": 1},
]
comments = [
    {"subreddit": "testsub", "post_id": "p1", "content": "Totally agree", "created_utc": 1690000100, "score": 5},
    {"subreddit": "testsub", "post_id": "p1", "content": "Best value", "created_utc": 1690000200, "score": 3},
    {"subreddit": "testsub", "post_id": "p2", "content": "Same here", "created_utc": 1690001100, "score": 4},
]

posts_df = pd.DataFrame(posts)
comments_df = pd.DataFrame(comments)

# Build teams (uses your function)
teams = _build_teams_from_posts(posts_df, comments_df, brand="testbrand", top_n_comments=5)
print("Built teams (count):", len(teams))
if teams:
    print("Example team:", teams[0])

# Call real ML at ML_URL (or mock) and get sentiment
ML_URL = os.environ.get("ML_URL", "http://localhost:8080")
r = requests.post(f"{ML_URL}/get_sentiment", json={"teams": teams}, timeout=20)
r.raise_for_status()
sentiments = r.json().get("sentiment", [])
print("ML returned sentiments:", sentiments)

# compute per-team averages
avg_sentiments = []
for s in sentiments:
    if s:
        avg_sentiments.append(sum(map(float, s)) / len(s))
    else:
        avg_sentiments.append(0.0)

print("Avg sentiments:", avg_sentiments)

# create a quick histogram and open it
fig = px.histogram(x=avg_sentiments, nbins=10, title="Synthetic test histogram")
out = "synthetic_histogram.html"
fig.write_html(out, auto_open=True)
print("Wrote", out)
