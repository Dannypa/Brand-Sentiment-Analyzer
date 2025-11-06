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

from charts.latest_histogram import histogram_combined, histogram_sentiment
from charts.time_series import time_series_sentiment
from charts.word_cloud import word_cloud
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
# print(requests.get("http://localhost:10001/docs").json())


def get_charts_inner(brands: list[str]) -> list[Chart]:
    charts = []

    try:
        charts.extend(
            [
                Chart(
                    title="Sentiment histogram",
                    plotly_json=histogram_sentiment(brands),
                ),
                # Chart(title="Combined histogram", plotly_json=histogram_combined([brand])),
                Chart(
                    title="Sentiment time series",
                    plotly_json=time_series_sentiment(brands),
                ),
                # Chart(title="Views time series", plotly_json=time_series_views([brand])),
                # Chart(title="Combined time series", plotly_json=time_series_combined([brand])),
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating charts: {e}")

    return charts


@api.get("/charts")
def get_charts(brand: str) -> list[Chart]:
    return get_charts_inner([brand])


@api.post("/charts/multibrand")
def get_charts_multibrand(brands: list[str]) -> list[Chart]:
    return get_charts_inner(brands)


@api.get("/charts/wordcloud")
def get_word_cloud(brand: str):
    image = word_cloud([brand])
    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return StreamingResponse(img_bytes, media_type="image/png")
