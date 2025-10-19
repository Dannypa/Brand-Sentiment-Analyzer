from fastapi import FastAPI, Query
from fastapi.exceptions import HTTPException
from pydantic import BaseModel, JsonValue
import plotly.express as px
import json
import requests
from typing import Optional, Annotated
import os
from dotenv import load_dotenv

load_dotenv()


ML_URL = os.environ.get("ML_URL", "http://ml:8080/get_sentiment")  # todo: env var

api = FastAPI()
# print(requests.get("http://localhost:10001/docs").json())


class Chart(BaseModel):
    title: Optional[str]
    plotly_json: JsonValue


@api.get("/charts")
def get_chart(
    brand: str, topics: Annotated[list[str], Query()] = []
) -> list[
    Chart
]:  # [] as default argument... is it ok? took from documentation, so probably fine?
    sentiment = requests.post(
        ML_URL,
        data=json.dumps(
            {"teams": [{"brand": brand, "texts": [f"{brand} cool", f"{brand} sucks"]}]}
        ),
    ).json()
    print(sentiment)
    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    json_fig_str = fig.to_json()

    if json_fig_str is None:
        raise HTTPException(status_code=404, detail="Figure not found for some reason")

    return [Chart(title="Sample chart.", plotly_json=json.loads(json_fig_str))]
