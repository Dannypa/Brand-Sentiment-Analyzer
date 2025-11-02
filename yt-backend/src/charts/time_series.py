import plotly.express as px
import plotly.io as pio
import datetime as dt
from dateutil.relativedelta import relativedelta
from ytapi import search_videos, get_comments
from dataclasses import dataclass
import pandas as pd
from ml import get_sentiment


QUERY_SPAN = relativedelta(months=12)
OLDEST_DATE = dt.datetime.now() - relativedelta(years=1)
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

@dataclass
class Video:
    title: str
    vid: str
    published_at: dt.datetime

def get_videos(brand: str, start_date: dt.datetime, end_date: dt.datetime):
    # print("in get_videos")
    # print(QUERY_SUFFIXES)
    # for suff in QUERY_SUFFIXES: 
        # print(f"There is a suff: {suff}")
    result = []
    for suffix in QUERY_SUFFIXES:
        # print("inside for loop....")
        query = brand + suffix
        # print(f"query: {query}")
        # print(start_date, end_date)
        videos = search_videos(query, start_date=start_date, end_date=end_date)
        for video in videos.items:
            title = video.snippet.title
            vid = video.id.videoId
            published_at = video.snippet.publishedAt
            result.append(Video(title, vid, published_at))
    return result


def get_comment_texts(vid: str) -> list[str]:
    comments = []
    comments_resp = get_comments(vid)
    for comment_thread in comments_resp.items:
        comments.append(comment_thread.snippet.topLevelComment.snippet.textOriginal) # todo: like count?
    return comments


def video_sentiment(video: Video) -> float:
    # print("here lol")
    # print(get_sentiment([video.title]))
    # print("after here lol")
    title_sentiment = float(get_sentiment([video.title])[0])
    # print("Sentiment of the title:", title_sentiment)

    comment_sentiment = get_sentiment(get_comment_texts(video.vid))
    # print("Comment sentiment: ", comment_sentiment)

    return (title_sentiment + sum(comment_sentiment)) / (len(comment_sentiment) + 1) # weight of 1 comment to title for now; change later
   
def get_all_videos(brands: list[str]) -> dict[str, list[Video]]:
        result = {brand: [] for brand in brands}
        for brand in brands:
            for start_date in get_download_timerange():
                end_date = start_date + QUERY_SPAN
                result.setdefault(brand, []).extend(get_videos(brand, start_date, end_date))
                
        return result


def time_series_sentiment(brands: list[str]) -> str:
    dates = [] # todo: query vids once??
    sentiment = {brand: [] for brand in brands}

    videos = get_all_videos(brands)
    print(len(videos))

    for start_date in get_visualisation_timerange():
        dates.append(start_date)
        end_date = start_date + VISUALISATION_SECTION

        for brand in brands:

            # print(brand, start_date)
            section = [video for video in videos[brand] if start_date.timestamp() <= video.published_at.timestamp() <= end_date.timestamp()]
            # print(videos)
            temp_sentiment = []
            for video in section:
                print(video)
                try:
                    temp_sentiment.append(video_sentiment(video))
                except Exception as e:
                    print(e)
                    continue
            if len(temp_sentiment) == 0:
                sentiment[brand].append(0)  # not ideal, todo: fix so that it just skips the month
            else:
                sentiment[brand].append(sum(temp_sentiment) / len(temp_sentiment))
        

    df = pd.DataFrame(
        {
            "dates": dates,
            **sentiment
        }
    )
    fig = px.line(df, x="dates", y=brands)
    json_res = fig.to_json()
    if json_res is None:
        raise ValueError("Failed to produce a plot json.")
    return json_res

def time_series_views() -> str:
    df = px.data.tips() # returns a pandas DataFrame
    fig = px.histogram(df, x="total_bill")
    return pio.to_json(fig)

def time_series_combined() -> str:
    df = px.data.tips() # returns a pandas DataFrame
    fig = px.histogram(df, x="total_bill")
    return pio.to_json(fig)
