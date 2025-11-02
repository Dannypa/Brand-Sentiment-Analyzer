from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, JsonValue
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
# from charts.latest_histogram import histogram_sentiment, histogram_combined
from charts.time_series import time_series_sentiment, time_series_views, time_series_combined

load_dotenv()


ML_URL = os.environ.get("ML_URL")  # todo: env var

api = FastAPI()
# print(requests.get("http://localhost:10001/docs").json())


@api.get("/charts")
def get_charts(brand: str) -> list[Chart]:

    charts = []

    try:
        charts.extend(
            [
                # Chart(title="Sentiment histogram", plotly_json=histogram_sentiment()),
                # Chart(title="Combined histogram", plotly_json=histogram_combined()),
                Chart(title="Sentiment time series", plotly_json=time_series_sentiment([brand])),
#                Chart(title="Views time series", plotly_json=time_series_views()),
#                Chart(title="Combined time series", plotly_json=time_series_combined()),
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating charts: {e}")

    return charts

@api.post("/charts/multibrand")
def get_charts_multibrand(brands: list[str]) -> list[Chart]:
    
    charts = []

    return charts
