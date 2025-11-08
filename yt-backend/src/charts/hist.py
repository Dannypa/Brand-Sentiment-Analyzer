from services import get_all_video_data
from datetime import datetime
import datetime as dt
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.io as pio
import plotly.graph_objects as go

def hist(brands: list[str], conn: psycopg2):
    data = get_all_video_data(conn, brands[0], 40, datetime.now() - dt.timedelta(days=30), datetime.now())
    
    df = pd.DataFrame([vars(video) for video in data])
    fig = px.histogram(df, x='avg_sentiment', nbins=20, title='Histogram of Average Sentiment')

    return pio.to_json(fig)