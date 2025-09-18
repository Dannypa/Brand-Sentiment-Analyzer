import os
import dotenv
import pandas as pd
import numpy as np
import re
from googleapiclient.discovery import build
from models import *

#dotenv.load_dotenv()

#key = os.getenv("KEY")
key = "AIzaSyDVOztLv-rBY-XBpw1DXzaqIFdzkI3AvQE" #"AIzaSyCrB5Q4wgPvIEAcrf25UtTT7f98evqrvCA"

youtube = build('youtube', 'v3', developerKey=key)

def search_videos(query, max_results=50, start_date=None, end_date=None, page_token = None):
    request = youtube.search().list(
        q=query,
        part='id,snippet',
        type='video',
        maxResults=max_results,
        order='relevance',
        relevanceLanguage = 'en',
        publishedAfter=start_date,
        publishedBefore=end_date,
        videoDuration='medium',
        pageToken = page_token
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
