import plotly.express as px
from pydantic import JsonValue

def time_series_sentiment() -> JsonValue:
    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    json_fig_str = fig.to_json()
    return json_fig_str

def time_series_views() -> JsonValue:
    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    json_fig_str = fig.to_json()
    return json_fig_str

def time_series_combined() -> JsonValue:
    fig = px.scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16])
    json_fig_str = fig.to_json()
    return json_fig_str