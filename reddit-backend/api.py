import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from charts.latest_histogram import histogram_sentiment
from charts.time_series import time_series_sentiment
from models import Chart

load_dotenv()


ML_URL = os.environ.get("ML_URL")  # todo: env var

api = FastAPI()
# print(requests.get("http://localhost:10001/docs").json())


# @api.get("/charts")
# def get_charts(brand: str) -> list[Chart]:

#     charts = []

#     try:
#         # TODO: for now, seperate brands by commas. either implement something later or let it be
#         brands = brand.split(',')
#         print("List of brands:", brands)
#         charts.extend(
#             [
#                 Chart(title="Sentiment histogram", plotly_json=histogram_sentiment(brands)),
#                 # Chart(title="Combined histogram", plotly_json=histogram_combined(brands)),
#                 Chart(title="Sentiment time series", plotly_json=time_series_sentiment(brands)),
#                 # Chart(title="Views time series", plotly_json=time_series_views(brands)),
#                 # Chart(title="Combined time series", plotly_json=time_series_combined(brands)),
#             ]
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating charts: {e}")

#     return charts

# @api.post("/charts/multibrand")
# def get_charts_multibrand(brands: list[str]) -> list[Chart]:

#     charts = []

#     return charts


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
