from fastapi import FastAPI
from fastapi.exceptions import HTTPException
import os
from models import Chart
from dotenv import load_dotenv
from charts.latest_histogram import histogram_sentiment
from charts.time_series import time_series_sentiment
from charts.topic_chart import topic_chart
load_dotenv()


ML_URL = os.environ.get("ML_URL")  # todo: env var

api = FastAPI()
# print(requests.get("http://localhost:10001/docs").json())


@api.get("/charts")
def get_charts(brand: str, subreddits: str) -> list[Chart]:

    charts = []
    sub_list = [s.strip() for s in subreddits.split(",")] if subreddits else None

    try:
        charts.extend(
            [
                Chart(title="Sentiment histogram (top posts)", plotly_json=histogram_sentiment(brand, subreddits=sub_list), fetch_limit=20), # increase fetch limit later
                Chart(title="Sentiment time series (keyword search)", plotly_json=time_series_sentiment(brand, subreddits=sub_list)),
                Chart(title="Topic chart (keyword search)", plotly_json=topic_chart(brand, subreddits=sub_list)),
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating charts: {e}")

    return charts

@api.post("/charts/multibrand")
def get_charts_multibrand(brands: list[str]) -> list[Chart]:
    
    charts = []

    return charts

