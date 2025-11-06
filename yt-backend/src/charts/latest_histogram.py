from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.io as pio

from ml import get_sentiment
from models import (
    CommentListResponse,
    SearchListResponse,
    SearchQuery,
    VideoListResponse,
)
from services import get_comment_reply_dict
from ytapi import execute_search_query, get_comments, get_video_details


# kinda the estimated distribution kde line
def histogram_sentiment(brands: list[str]) -> str:
    video_df, _ = get_scaled_dfs(brands, days=30)
    print(video_df)

    if video_df is None or video_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis_title="Sentiment",
            yaxis_title="Number of videos",
            template="plotly_white",
        )
        return pio.to_json(fig)
    else:
        brands_sort = sorted(video_df["brand"].unique())
        hist_data = []
        group_labels = []
        for b in brands_sort:
            data = video_df[video_df["brand"] == b]["avg_sentiment"].fillna(0).tolist()
            if not data or np.all(data == 0):
                print(f"No avg_sentiment data for brand {b}")
                data = [0, 0.0001]
            data = np.clip(data, -1, 1)
            hist_data.append(data)
            group_labels.append(b)

        if not hist_data or not group_labels:
            fig = go.Figure()
            fig.update_layout(
                title="No data available",
                xaxis_title="Sentiment",
                yaxis_title="Number of videos",
                template="plotly_white",
            )
            return pio.to_json(fig)
        else:
            try:
                fig = ff.create_distplot(
                    hist_data,
                    group_labels,
                    curve_type="kde",
                    bin_size=0.1,
                    show_rug=False,
                )
            except Exception as e:
                print(f"Error: {e}")
                fig = go.Figure()
                fig.update_layout(
                    title="No data available",
                    xaxis_title="Sentiment",
                    yaxis_title="Number of videos",
                    template="plotly_white",
                )
                return pio.to_json(fig)
            palette = px.colors.qualitative.Vivid
            for i in range(len(group_labels)):
                hist_trace = fig.data[i * 2]
                kde_trace = fig.data[i * 2 + 1]
                color = palette[i % len(palette)]

                # hist_trace.marker.color = color
                # kde_trace.line.color = color

            fig.update_layout(
                title="Sentiment Distribution (estimated)",
                xaxis_title="Sentiment (-1 to 1)",
                yaxis_title="Number of videos",
            )

            fig.update_layout(template="plotly_white")

            return pio.to_json(fig)


def histogram_combined(brands: list[str]) -> str:
    video_df, _ = get_scaled_dfs(brands, days=30)
    print(video_df)

    if video_df is None or video_df.empty:
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis_title="Sentiment",
            yaxis_title="Number of videos",
            template="plotly_white",
        )
        return pio.to_json(fig)
    else:
        brands_sort = sorted(video_df["brand"].unique())
        hist_data = []
        group_labels = []
        for b in brands_sort:
            data = video_df[video_df["brand"] == b]["scaled_result"].fillna(0).tolist()
            if not data or np.all(data == 0):
                print(f"No avg_sentiment data for brand {b}")
                data = [0, 0.0001]
            data = np.clip(data, -1, 1)
            hist_data.append(data)
            group_labels.append(b)

        if not hist_data or not group_labels:
            fig = go.Figure()
            fig.update_layout(
                title="No data available",
                xaxis_title="Sentiment",
                yaxis_title="Number of videos",
                template="plotly_white",
            )
            return pio.to_json(fig)
        else:
            try:
                fig = ff.create_distplot(
                    hist_data,
                    group_labels,
                    curve_type="kde",
                    bin_size=0.1,
                    show_rug=False,
                )
            except Exception as e:
                print(f"Error: {e}")
                fig = go.Figure()
                fig.update_layout(
                    title="No data available",
                    xaxis_title="Sentiment",
                    yaxis_title="Number of videos",
                    template="plotly_white",
                )
                return pio.to_json(fig)
            palette = px.colors.qualitative.Vivid
            for i in range(len(group_labels)):
                hist_trace = fig.data[i * 2]
                kde_trace = fig.data[i * 2 + 1]
                color = palette[i % len(palette)]

                # hist_trace.marker.color = color
                # kde_trace.line.color = color

            fig.update_layout(
                title="Sentiment Distribution (estimated, weighted by attention)",
                xaxis_title="Sentiment (-1 to 1)",
                yaxis_title="Number of videos",
            )

            fig.update_layout(template="plotly_white")

            return pio.to_json(fig)


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
            page_token=page_token,
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

    print(
        f"Fetched {len(brand_videos)} videos for {brand}. brand {brand_videos[0].snippet.title.lower()}"
    )
    return brand_videos


def process_video(vid, brand: str, max_comments: int = 50):
    video_id = vid.id.videoId
    video_title = vid.snippet.title
    video_publish = vid.snippet.publishedAt

    views = 0
    likes = 0
    comments_count = 0
    try:
        details = get_video_details(video_id)
        details = VideoListResponse(**details)
        stats = details.items[0].statistics
        views = int(stats.viewCount or 0)
        likes = int(stats.likeCount or 0)
        comments_count = int(stats.commentCount or 0)
    except Exception as e:
        print(f"error in stats, video {video_id}: {e}")

    comment_texts = []
    if comments_count > 0:
        try:
            vid_comments_raw = get_comments(video_id, max_results=max_comments)
            if isinstance(vid_comments_raw, CommentListResponse):
                vid_comments = vid_comments_raw
            else:
                vid_comments = CommentListResponse(**vid_comments_raw)

            comment_reply_dict = get_comment_reply_dict(vid_comments)
            for top_level, replies in comment_reply_dict.items():
                comment_texts.append(top_level)
                comment_texts.extend(replies)
        except Exception as e:
            print(f"error in comments, video {video_id}: {e}")

    title_sent = 0.0
    avg_comment_sent = 0.0
    avg_sentiment = 0.0
    total_sent = 0.0
    try:
        if video_title:
            title_sent = get_sentiment([video_title])[0]
        if comment_texts:
            comment_sent_list = get_sentiment(comment_texts)
            avg_comment_sent = (
                sum(comment_sent_list) / len(comment_sent_list)
                if comment_sent_list
                else 0
            )
    except Exception as e:
        print(f"sentiments, video {video_id}: {e}")

    avg_sentiment = (title_sent + avg_comment_sent) / 2

    w_likes = 0.012
    w_comments = 0.988
    total_sent = (
        title_sent * likes * w_likes + avg_comment_sent * comments_count * w_comments
    )

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
        "total_sentiment": total_sent,
    }

    comments_df = [
        {"video_id": video_id, "brand": brand, "text": t} for t in comment_texts
    ]
    return video_data, comments_df


def get_scaled_dfs(brands: list[str], days: int):
    vids_list = []
    total_comments = []

    for brand in brands:
        brand_rows = []
        brand_videos = fetch_videos(brand, days)
        if not brand_videos:
            print(f"No videos found for {brand}")
        else:
            # Exclude video without brand in the title
            for vid in brand_videos:
                title = vid.snippet.title.lower()
                if brand.lower() not in title:
                    continue
                try:
                    video_data, comments = process_video(vid, brand)
                except Exception as e:
                    print(f"error in process video, video {vid.id.videoId}: {e}")
                    continue
                brand_rows.append(video_data)
                total_comments.extend(comments)
        if not brand_rows:
            brand_rows.append(
                {
                    "video_id": None,
                    "video_title": None,
                    "brand": brand,
                    "publishedAt": None,
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "sentiment_comments": 0.0,
                    "sentiment_title": 0.0,
                    "avg_sentiment": 0.0,
                    "total_sentiment": 0.0,
                    "scaled_result": 0.0,
                }
            )
        vids_list.extend(brand_rows)

    video_df = pd.DataFrame(vids_list)

    comment_df = pd.DataFrame(total_comments)
    if comment_df.empty:
        comment_df = pd.DataFrame(columns=["video_id", "brand", "text"])
    comment_df = comment_df.drop_duplicates(subset=["video_id", "text"])

    video_df = video_df.drop_duplicates(["video_id", "brand"])
    min_sent = video_df["total_sentiment"].min()
    max_sent = video_df["total_sentiment"].max()
    if min_sent == max_sent:
        video_df["scaled_result"] = 0
    else:
        video_df["scaled_result"] = video_df["total_sentiment"] / max(
            abs(min_sent), abs(max_sent)
        )

    return video_df, comment_df
