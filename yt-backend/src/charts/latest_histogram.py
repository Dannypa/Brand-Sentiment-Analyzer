import plotly.express as px
import plotly.figure_factory as ff
import plotly.io as pio
from pydantic import JsonValue
from services import remove_videos_without_brand_title, remove_videos_without_comments, video_to_dataframe, get_comment_reply_dict
import numpy as np
import pandas as pd
import requests
import json
from datetime import datetime, timedelta, timezone
from ytapi import get_video_details, get_comments, execute_search_query
from models import CommentListResponse, SearchListResponse, VideoListResponse, Team, SentimentQuery, SearchQuery
from ml import get_sentiment
#kinda the estimated distribution kde line
def histogram_sentiment(brands: list[str]) -> str:
    video_df, _ = get_scaled_dfs(brands, days = 30)
    if video_df is None or video_df.empty:
        raise ValueError("No data available.")
    brands_sort = sorted(video_df["brand"].unique())
    hist_data = [video_df[video_df["brand"] == b]["avg_sentiment"].tolist() for b in brands_sort]
    group_labels = brands_sort
    palette = px.colors.qualitative.Vivid

    fig = ff.create_distplot(hist_data,
                             group_labels, 
                             curve_type='kde', 
                             bin_size = 0.1,
                             show_rug = False)
    
    for i, trace in enumerate(fig.data):
        if trace.type == "scatter": 
            trace.line.color = palette[i%len(palette)]
        elif trace.type == "histogram": 
            trace.marker.color = palette[i%len(palette)]

    fig.update_layout(title="Sentiment Distribution (estimated)",
        xaxis_title="Sentiment (-1 to 1)",
        yaxis_title="Number of videos")
    
    fig.update_layout(template = 'plotly_white')

    json_fig_str = pio.to_json(fig)
    if json_fig_str is None:
        raise ValueError("Failed to produce a plot json.")
    return json_fig_str

def histogram_combined(brands: list[str]) -> str:
    video_df, _ = get_scaled_dfs(brands, days = 30)
    if video_df is None or video_df.empty:
        raise ValueError("No data available.")
    brands_sort = sorted(video_df["brand"].unique())
    hist_data = [video_df[video_df["brand"] == b]["scaled_result"].tolist() for b in brands_sort]
    group_labels = brands_sort
    palette = px.colors.qualitative.Vivid

    fig = ff.create_distplot(hist_data,
                             group_labels, 
                             curve_type='kde',
                             bin_size = 0.1,
                             show_rug = False)    
    for i, trace in enumerate(fig.data):
        if trace.type == "scatter": 
            trace.line.color = palette[i%len(palette)]
        elif trace.type == "histogram": 
            trace.marker.color = palette[i%len(palette)]

    fig.update_layout(title="Sentiment Distribution (estimated, weighted by attention)",
        xaxis_title="Sentiment (-1 to 1)",
        yaxis_title="Number of videos")
    
    fig.update_layout(template = 'plotly_white')
    
    json_fig_str = pio.to_json(fig)
    if json_fig_str is None:
        raise ValueError("Failed to produce a plot json.")
    return json_fig_str


def fetch_sentiment(videos: list[dict]): 
    all_sentiments = []
    for v in videos:
        texts = v.get("texts") or []
        all_sentiments.append(get_sentiment(texts))
    return all_sentiments

def time_period(d: int):
    today = datetime.now(timezone.utc)
    some_days_ago = today - timedelta(days=d)
    return today, some_days_ago

def fetch_videos(brand: str, days: int, pages: int = 2):
    today, some_days_ago = time_period(days)
    q = f"{brand.lower()} bad OR {brand.lower()} good OR {brand.lower()} "
    page_token = None
    brand_videos = []
    for i in range(pages):
        query = SearchQuery(
            q=q,
            max_results=50,
            published_after=some_days_ago,
            published_before=today,
            page_token=page_token
        )
        try: 
            videos = execute_search_query(query)
        except Exception as e: 
            print(e)
            break
        try: 
            videos = SearchListResponse(**videos)
        except Exception as e: 
            print(e)
            continue

        brand_videos.extend(videos.items)
        page_token = videos.nextPageToken
        if not page_token:
            break

    print(f"Fetched {len(brand_videos)} videos for {brand}.")
    return brand_videos 


def process_video(vid, brand: str, max_comments: int = 50):
    video_id = vid.id.videoId
    video_title = vid.snippet.title
    video_publish = vid.snippet.publishedAt

    details = get_video_details(video_id)
    details = VideoListResponse(**details)
    stats = details.items[0].statistics

    views = int(stats.viewCount or 0)
    likes = int(stats.likeCount or 0)
    comments_count = int(stats.commentCount or 0)

    vid_comments = get_comments(video_id, max_results=max_comments)
    vid_comments = CommentListResponse(**vid_comments)
    comment_reply_dict = get_comment_reply_dict(vid_comments)

    comment_texts = []
    for top_level, replies in comment_reply_dict.items():
        comment_texts.append(top_level)
        comment_texts.extend(replies)

    teams = [{"brand": brand, "title": video_title, "texts": comment_texts}]
    sentiments = fetch_sentiment(teams)

    title_sent = sentiments[0][0] if sentiments[0] else 0
    avg_comment_sent = sum(sentiments[0][1:]) / len(sentiments[0][1:]) if len(sentiments[0]) > 1 else 0

    avg_sentiment = (title_sent + avg_comment_sent)/2

    w_likes = 0.012
    w_comments = 0.988
    total_sent = title_sent * likes * w_likes + avg_comment_sent * comments_count * w_comments

    video_data = {
        "video_id": video_id,
        "video_title": video_title,
        "brand": brand,
        "publishedAt": video_publish,
        "views": views,
        "likes": likes,
        "comments": comments_count,
        "sentiment_comments": avg_comment_sent,
        "sentiment_title": title_sent,
        "avg_sentiment": avg_sentiment,
        "total_sentiment": total_sent
    }

    comments_df = [{"video_id": video_id, "brand": brand, "text": t} for t in comment_texts]

    return video_data, comments_df


def get_scaled_dfs(brands: list[str], days:int):
    vids_list = []
    total_comments = []
    
    for brand in brands:
        brand_videos = fetch_videos(brand, days)
        # Exclude video without brand in the title, without comments
        vid_df = video_to_dataframe(SearchListResponse(items = brand_videos, kind="", etag= "", regionCode="", pageInfo= {"totalResults": 0, "resultsPerPage": 0}))
        vid_df = remove_videos_without_brand_title(vid_df, brand)        
        vid_df = remove_videos_without_comments(vid_df)
        brand_videos = [v for v in brand_videos if v.id.videoId in vid_df["video_id"].values]
        for vid in brand_videos:
            video_data, comments = process_video(vid, brand,max_comments = 50)
            if video_data is None:
                continue
            vids_list.append(video_data)
            total_comments.extend(comments)
    
    video_df = pd.DataFrame(vids_list)
    if video_df.empty:
        print("No satisfied videos to work with.")
        video_df = pd.DataFrame(columns=[
        "video_id", "video_title", "brand", "publishedAt",
        "views", "likes", "comments", "sentiment_comments",
        "sentiment_title", "avg_sentiment", "total_sentiment",
        "scaled_result"
    ])
        
        comment_df = pd.DataFrame(columns=["video_id","brand","publishedAt","comment_id","top_level_id","text","sentiment"])
        return video_df, comment_df

    comment_df = pd.DataFrame(total_comments)

    if comment_df.empty:
        comment_df = pd.DataFrame(columns=["video_id","brand","publishedAt","comment_id","top_level_id","text","sentiment"])
    
    video_df = video_df.drop_duplicates(["video_id", "brand"])
    comment_df = comment_df.drop_duplicates(["comment_id", "brand"])
    min_sent = video_df["total_sentiment"].min()
    max_sent = video_df["total_sentiment"].max()
    if min_sent == max_sent:
        video_df["scaled_result"] = 0
    else:
        video_df["scaled_result"] = video_df["total_sentiment"]/max(abs(min_sent), abs(max_sent))

    return video_df, comment_df
