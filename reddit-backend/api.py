import os

from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
import psycopg2
from psycopg2 import pool

from charts.latest_histogram import histogram_sentiment
from charts.time_series import time_series_sentiment
from models import Chart

load_dotenv()


ML_URL = os.environ.get("ML_URL")  # todo: env var

api = FastAPI()
db_pool = None
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
                    plotly_json=histogram_sentiment(conn, brands),
                ),
                # Chart(title="Combined histogram", plotly_json=histogram_combined([brand])),
                Chart(
                    title="Sentiment time series",
                    plotly_json=time_series_sentiment(conn, brands),
                ),
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
