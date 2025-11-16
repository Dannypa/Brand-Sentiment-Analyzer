import asyncio
import datetime as dt
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

# import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import psycopg2
from dateutil.relativedelta import relativedelta

from services import get_all_video_data


async def get_by_start_date(start_date: datetime, brand: str, conn):
    end_date = start_date + QUERY_SPAN
    videos = await get_all_video_data(conn, brand, 5, start_date, end_date)
    return videos


async def time_series_sentiment(brands: list[str], conn: psycopg2):
    brand_videos = {}

    for brand in brands:
        brand_videos[brand] = []

        tasks = [
            get_by_start_date(start_date, brand, conn)
            for start_date in get_download_timerange()
        ]
        for result in await asyncio.gather(*tasks):
            brand_videos[brand].extend(result)

    if not any(brand_videos.values()):
        fig = go.Figure()
        fig.update_layout(
            title="No data available",
            xaxis_title="Month",
            yaxis_title="Sentiment",
            template="plotly_white",
        )
        return pio.to_json(fig)

    figures = []
    for brand in brands:
        if not brand_videos[brand]:
            continue

        try:
            video_df = pd.DataFrame(
                [
                    {
                        "video_id": v.video_id,
                        "brand": v.query,
                        "published_at": v.datetime,
                        "avg_sentiment": v.avg_sentiment or 0.0,
                    }
                    for v in brand_videos[brand]
                ]
            )

            video_df["published_at"] = pd.to_datetime(
                video_df["published_at"], errors="coerce"
            )
            video_df = video_df.dropna(subset=["published_at"])

            video_df["month"] = video_df["published_at"].dt.to_period("M")
            monthly_df = video_df.groupby("month")["avg_sentiment"].mean().reset_index()
            monthly_df["month"] = monthly_df["month"].dt.to_timestamp()
            monthly_df.sort_values(by="month", inplace=True)

            figures.append(
                go.Scatter(
                    x=monthly_df["month"],
                    y=monthly_df["avg_sentiment"],
                    name=brand,
                    connectgaps=True,
                )
            )
        except Exception as e:
            print(f"Error processing brand {brand}: {e}")
            continue

    if not figures:
        fig = go.Figure()
        fig.update_layout(
            title="No valid data available",
            xaxis_title="Month",
            yaxis_title="Sentiment",
            template="plotly_white",
        )
        return pio.to_json(fig)

    fig = go.Figure(data=figures)
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Sentiment",
        title="Sentiment over time",
        template="plotly_white",
    )

    return pio.to_json(fig)


QUERY_SPAN = relativedelta(months=4)
OLDEST_DATE = dt.datetime.now() - relativedelta(months=24)


def get_timerange(step: relativedelta):
    current_date = OLDEST_DATE
    while current_date < dt.datetime.now():
        yield current_date
        current_date += step


def get_download_timerange():
    yield from get_timerange(QUERY_SPAN)


"""
QUERY_SPAN = relativedelta(months=4)
OLDEST_DATE = dt.datetime.now() - relativedelta(months=24)
QUERY_SUFFIXES = ("",)
# QUERY_SUFFIXES = ("", " good", " bad")

VISUALISATION_SECTION = relativedelta(months=1)


def get_timerange(step: relativedelta):
    current_date = OLDEST_DATE
    while current_date < dt.datetime.now():
        yield current_date
        current_date += step


def get_download_timerange():
    yield from get_timerange(QUERY_SPAN)


def get_visualisation_timerange():
    yield from get_timerange(VISUALISATION_SECTION)


@dataclass(frozen=True)
class Video:
    title: str
    vid: str
    published_at: dt.datetime


def get_videos(brand: str, start_date: dt.datetime, end_date: dt.datetime):
    # print("in get_videos")
    # print(QUERY_SUFFIXES)
    # for suff in QUERY_SUFFIXES:
    # print(f"There is a suff: {suff}")
    result = set()
    for suffix in QUERY_SUFFIXES:
        # print("inside for loop....")
        query = brand + suffix
        # print(f"query: {query}")
        # print(start_date, end_date)
        videos = search_videos(query, start_date=start_date, end_date=end_date)
        for video in videos.items:
            title = video.snippet.title
            if brand.lower() not in title.lower():
                continue  # otherwise Vlad and fucking Niki are going to overflow my results
            vid = video.id.videoId
            published_at = video.snippet.publishedAt
            result.add(Video(title, vid, published_at))
    return list(result)


def get_comment_texts(vid: str) -> list[str]:
    comments = []
    comments_resp = get_comments(vid)
    for comment_thread in comments_resp.items:
        comments.append(
            comment_thread.snippet.topLevelComment.snippet.textOriginal
        )  # todo: like count?
    return comments


def video_sentiment(video: Video) -> float:
    # print("here lol")
    # print(get_sentiment([video.title]))
    # print("after here lol")

    title_sentiment = float(get_sentiment([video.title])[0])
    # print("Sentiment of the title:", title_sentiment)

    comment_sentiment = get_sentiment(get_comment_texts(video.vid))
    # print("Comment sentiment: ", comment_sentiment)

    return (title_sentiment + sum(comment_sentiment)) / (
        len(comment_sentiment) + 1
    )  # weight of 1 comment to title for now; change later


def get_all_videos(brands: list[str]) -> dict[str, list[Video]]:
    result = {brand: [] for brand in brands}
    for brand in brands:
        for start_date in get_download_timerange():
            end_date = start_date + QUERY_SPAN
            result.setdefault(brand, []).extend(get_videos(brand, start_date, end_date))

    return result


def time_series_sentiment(brands: list[str]) -> str:
    sentiment = {brand: [] for brand in brands}
    dates = {brand: [] for brand in brands}

    videos = get_all_videos(brands)
    print(len(videos))

    for start_date in get_visualisation_timerange():
        end_date = start_date + VISUALISATION_SECTION

        for brand in brands:
            # print(brand, start_date)
            section = [
                video
                for video in videos[brand]
                if start_date.timestamp()
                <= video.published_at.timestamp()
                <= end_date.timestamp()
            ]
            # print(videos)
            temp_sentiment = []
            for video in section:
                print(video)
                try:
                    temp_sentiment.append(video_sentiment(video))
                except Exception as e:
                    print(e)
                    continue

            if len(temp_sentiment) != 0:
                sentiment[brand].append(sum(temp_sentiment) / len(temp_sentiment))
                dates[brand].append(
                    start_date
                )  # todo: months, cuz now it shows random date on the tooltip
            # if len(temp_sentiment) == 0, we just skip the month

    # df = pd.DataFrame({"dates": dates, **sentiment})
    # fig = px.line(df, x="dates", y=brands)

    fig = go.Figure(
        data=[
            go.Scatter(x=dates[brand], y=sentiment[brand], name=brand)
            for brand in brands
        ],
        layout={
            "xaxis": {"title": "month"},
            "yaxis": {"title": "sentiment"},
            "title": "Sentiment over time",
        },
    )

    json_res = fig.to_json()
    if json_res is None:
        raise ValueError("Failed to produce a plot json.")
    return json_res


# def time_series_views() -> str:
#     df = px.data.tips() # returns a pandas DataFrame
#     fig = px.histogram(df, x="total_bill")
#     return pio.to_json(fig)

# def time_series_combined() -> str:
#     df = px.data.tips() # returns a pandas DataFrame
#     fig = px.histogram(df, x="total_bill")
#     return pio.to_json(fig)
"""
