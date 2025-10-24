import plotly.express as px
from pydantic import JsonValue

def histogram_sentiment() -> JsonValue:
    fig = px.histogram(x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    json_fig_str = fig.to_json()
    return json_fig_str

def histogram_combined() -> JsonValue:
    fig = px.histogram(x=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    json_fig_str = fig.to_json()
    return json_fig_str