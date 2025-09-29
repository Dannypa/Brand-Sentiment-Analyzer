import os
import dotenv
import pandas as pd
import numpy as np
import re
from googleapiclient.discovery import build
from models import *
import finnhub

dotenv.load_dotenv()

youtube_key = os.getenv("YOUTUBE_KEY")
finnhub_key = os.getenv("FINNHUB_KEY")

youtube = build('youtube', 'v3', developerKey=youtube_key)
finnhub = finnhub.Client(api_key=finnhub_key)

def search_videos(query, max_results=50, start_date=None, end_date=None):
    request = youtube.search().list(
        q=query,
        part='id,snippet',
        type='video',
        maxResults=max_results,
        order='relevance',
        publishedAfter=start_date,
        publishedBefore=end_date,
        videoDuration='medium',
    )
    response = request.execute()
    return response

def get_comments(video_id, max_results=50):
    request = youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id,
        maxResults=max_results,
        order='relevance',
    )
    response = request.execute()
    return response

def get_video_details(video_id):
    request = youtube.videos().list(
        part='statistics',
        id=video_id
    )
    response = request.execute()
    return response

def get_market_cap(brand_name):
    lookup = finnhub.symbol_lookup(brand_name)
    results = symbolLookup(**lookup)
    print(results)
    symbol = results.result[0].symbol

    company_profile = finnhub.company_profile2(symbol=symbol)
    company_profile = companyProfile(**company_profile)
    market_cap = company_profile.marketCapitalization
    return market_cap
