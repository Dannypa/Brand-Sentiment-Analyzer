import plotly.express as px
import plotly.io as pio
import datetime as dt
from dateutil.relativedelta import relativedelta
from ytapi import search_videos, get_comments
from dataclasses import dataclass
import pandas as pd

# todo: move to separate common file!!!!
def get_sentiment(texts: list[str]):
    import requests
    import json
    address = "http://ml:8080/get_sentiment"
    data = json.dumps([{"texts": texts}])
    sentiment = requests.post(address, data=data).json()[0]
    return sentiment


def get_timerange():
    oldest_year = dt.datetime.now().year - 2
    current_date = dt.datetime(year=oldest_year, month=1, day=1)
    while current_date < dt.datetime.now():
        yield current_date
        current_date += relativedelta(month=1)

@dataclass
class Video:
    title: str
    vid: str

def get_videos(brand: str, start_date: dt.datetime, end_date: dt.datetime):
    result = []
    for suffix in ["", " good", " bad"]:
        query = brand + suffix
        videos = search_videos(query, start_date=start_date, end_date=end_date)
        for video in videos.items:
            title = video.snippet.title
            vid = video.id.videoId 
            result.append(Video(title, vid))
    return result


def get_comment_texts(vid: str) -> list[str]:
    comments = []
    comments_resp = get_comments(vid)
    for comment_thread in comments_resp.items:
        comments.append(comment_thread.snippet.topLevelComment.snippet.textOriginal) # todo: like count?
    return comments



def video_sentiment(video: Video) -> float:
    title_sentiment = float(get_sentiment([video.title])[0])

    comment_sentiment = get_sentiment(get_comment_texts(video.vid))

    return (title_sentiment + sum(comment_sentiment)) / (len(comment_sentiment) + 1) # weight of 1 comment to title for now; change later
   

def time_series_sentiment(brands: list[str]) -> str:
    dates = [] # todo: query vids once??
    sentiment = {brand: [] for brand in brands}

    for start_date in get_timerange():
        end_date = start_date + relativedelta(month=1)
        dates.append(start_date)

        for brand in brands:
            
            videos = get_videos(brand, start_date, end_date)
            temp_sentiment = []
            for video in videos:
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
