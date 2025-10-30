import plotly.express as px
import plotly.io as pio

def histogram_sentiment() -> str:
    df = px.data.tips() # returns a pandas DataFrame
    fig = px.histogram(df, x="total_bill")
    return pio.to_json(fig)

def histogram_combined() -> str:
    df = px.data.tips() # returns a pandas DataFrame
    fig = px.histogram(df, x="total_bill")
    return pio.to_json(fig)