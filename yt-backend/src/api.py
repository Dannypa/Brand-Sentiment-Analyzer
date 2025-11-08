from fastapi import FastAPI, Depends
import io
import json
import os
from typing import Optional

import pandas as pd
import plotly.express as px
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, JsonValue
import io
import plotly.express as px
import json
import requests
from typing import Optional
import os
from models import Chart
from dotenv import load_dotenv
from ytapi import search_videos, get_comments, get_video_details
from services import video_to_dataframe, remove_videos_without_brand_title, remove_videos_without_comments
import pandas as pd
from charts.latest_histogram import histogram_sentiment, histogram_combined
from charts.time_series import time_series_sentiment

from charts.latest_histogram import histogram_combined, histogram_sentiment
from charts.time_series import time_series_sentiment
from charts.word_cloud import word_cloud
from charts.hist import hist
import psycopg2
from psycopg2 import pool
from models import Chart
from services import (
    remove_videos_without_brand_title,
    remove_videos_without_comments,
    video_to_dataframe,
)
from ytapi import get_comments, get_video_details, search_videos

load_dotenv()


ML_URL = os.environ.get("ML_URL")  # todo: env var

api = FastAPI()
db_pool = None
# print(requests.get("http://localhost:10001/docs").json())

@api.on_event("startup")
def startup():
    global db_pool
    db_pool = psycopg2.pool.SimpleConnectionPool(
        1,
        10,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
    )

@api.on_event("shutdown")
def shutdown():
    global db_pool
    if db_pool:
        db_pool.closeall()

def get_db_connection():
    global db_pool
    try:
        conn = db_pool.getconn()
        yield conn
    finally:
        db_pool.putconn(conn)


def get_charts_inner(brands: list[str], conn: psycopg2) -> list[Chart]:
    charts = []

    try:
        charts.extend(
            [
                Chart(
                    title="Sentiment histogram",
                    plotly_json=hist(brands, conn),
                ),
                # Chart(title="Combined histogram", plotly_json=histogram_combined([brand])),
                # Chart(
                #     title="Sentiment time series",
                #     plotly_json=time_series_sentiment(brands),
                # ),
                # Chart(title="Views time series", plotly_json=time_series_views([brand])),
                # Chart(title="Combined time series", plotly_json=time_series_combined([brand])),
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating charts: {e}")

    return charts


@api.get("/charts")
def get_charts(brand: str, conn=Depends(get_db_connection)) -> list[Chart]:
    return get_charts_inner([brand], conn)


@api.post("/charts/multibrand")
def get_charts_multibrand(brands: list[str], conn=Depends(get_db_connection)) -> list[Chart]:
    return get_charts_inner(brands, conn)


@api.get("/charts/wordcloud")
def get_word_cloud(brand: str):
    image = word_cloud([brand])
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return StreamingResponse(img_bytes, media_type="image/png")
