from fastapi import FastAPI
from fastapi.exceptions import HTTPException
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

    try:
        brands = [brand]
        charts.extend(
            [
                Chart(title="Sentiment histogram", plotly_json=histogram_sentiment(brands)),
                # Chart(title="Combined histogram", plotly_json=histogram_combined(brands)),
                # Chart(title="Sentiment time series", plotly_json=time_series_sentiment(brands)),
                # Chart(title="Views time series", plotly_json=time_series_views(brands)),
                # Chart(title="Combined time series", plotly_json=time_series_combined(brands)),
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating charts: {e}")

    return charts

@api.post("/charts/multibrand")
def get_charts_multibrand(brands: list[str]) -> list[Chart]:
    
    charts = []

    return charts

