import datetime as dt
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.io as pio
import psycopg2

from services import get_all_video_data


# kinda the estimated distribution kde line
async def histogram_sentiment(brands: list[str], conn: psycopg2) -> str:
    videos = []

    for b in brands:
        brand_videos = await get_all_video_data(
            conn, b, 100, datetime.now() - dt.timedelta(days=30), datetime.now()
        )
        if not brand_videos:
            continue
        videos.extend(brand_videos)

    if not videos:
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis_title="Sentiment",
            yaxis_title="Number of videos",
            template="plotly_white",
        )
        return pio.to_json(fig)

    video_df = pd.DataFrame(
        [
            {
                "video_id": v.video_id,
                "brand": v.query,
                "published_at": v.datetime,
                "views": v.views or 0,
                "likes": v.likes or 0,
                "comments": v.comments or 0,
                "avg_comment_sentiment": v.avg_comment_sentiment or 0.0,
                "title_sentiment": v.title_sentiment or 0.0,
                "avg_sentiment": v.avg_sentiment or 0.0,
                "weighted_sentiment": v.weighted_sentiment or 0.0,
            }
            for v in videos
        ]
    )
    print(video_df.head(5))

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

        fig.update_layout(
            title="Sentiment Distribution (estimated)",
            xaxis_title="Sentiment (-1 to 1)",
            yaxis_title="Number of videos",
        )

        fig.update_layout(template="plotly_white")

        return pio.to_json(fig)


def histogram_combined(brands: list[str], conn: psycopg2) -> str:
    videos = []

    for b in brands:
        brand_videos = get_all_video_data(
            conn, b, 100, datetime.now() - dt.timedelta(days=30), datetime.now()
        )
        if not brand_videos:
            continue
        videos.extend(brand_videos)

    if not videos:
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis_title="Sentiment",
            yaxis_title="Number of videos",
            template="plotly_white",
        )
        return pio.to_json(fig)

    video_df = pd.DataFrame(
        [
            {
                "video_id": v.video_id,
                "brand": v.query,
                "published_at": v.datetime,
                "views": v.views or 0,
                "likes": v.likes or 0,
                "comments": v.comments or 0,
                "avg_comment_sentiment": v.avg_comment_sentiment or 0.0,
                "title_sentiment": v.title_sentiment or 0.0,
                "avg_sentiment": v.avg_sentiment or 0.0,
                "weighted_sentiment": v.weighted_sentiment or 0.0,
            }
            for v in videos
        ]
    )

    brands_sort = sorted(video_df["brand"].unique())
    hist_data = []
    group_labels = []
    for b in brands_sort:
        data = video_df[video_df["brand"] == b]["weighted_sentiment"].fillna(0).tolist()
        if not data or np.all(data == 0):
            print(f"No weighted_sentiment data for brand {b}")
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

        fig.update_layout(
            title="Sentiment Distribution (estimated, weighted by attention)",
            xaxis_title="Sentiment (-1 to 1)",
            yaxis_title="Number of videos",
        )

        fig.update_layout(template="plotly_white")

        return pio.to_json(fig)
