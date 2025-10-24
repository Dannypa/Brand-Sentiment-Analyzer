from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, JsonValue
import plotly.express as px
import json
import os
from models import Chart
from dotenv import load_dotenv
from charts.latest_histogram import histogram_sentiment, histogram_combined
from charts.time_series import time_series_sentiment, time_series_views, time_series_combined

load_dotenv()


ML_URL = os.environ.get("ML_URL")  # todo: env var

api = FastAPI()
# print(requests.get("http://localhost:10001/docs").json())


@api.get("/charts")
def get_charts(brand: str) -> list[Chart]:

    charts = []
    print(f"Fetching charts for brand: {brand}")

    try:
        charts.extend(
            [
                Chart(title="Sentiment histogram", plotly_json=json.loads(histogram_sentiment())),
                Chart(title="Combined histogram", plotly_json=json.loads(histogram_combined())),
                Chart(title="Sentiment time series", plotly_json=json.loads(time_series_sentiment())),
                Chart(title="Views time series", plotly_json=json.loads(time_series_views())),
                Chart(title="Combined time series", plotly_json=json.loads(time_series_combined())),
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating charts: {e}")

    return charts

@api.get("/charts/multibrand")
def get_charts_multibrand(brands: list[str]) -> list[Chart]:
    
    charts = []

    return charts

