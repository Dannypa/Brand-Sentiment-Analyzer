from wordcloud import WordCloud
import numpy as np
from charts.latest_histogram import get_scaled_dfs
from services import video_to_dataframe, remove_videos_without_brand_title, remove_videos_without_comments
from ytapi import search_videos, get_comments, get_video_details
import pandas as pd
from PIL import Image

def word_cloud(brands: list[str]) -> Image:

    text = "test"
    for brand in brands:
        search_response = search_videos(f"{brand} bad", max_results=5)
        videos_df = video_to_dataframe(search_response)
        videos_df = remove_videos_without_comments(videos_df)
        videos_df = remove_videos_without_brand_title(videos_df, brand)
        all_comments = []
        for _, row in videos_df.iterrows():
            try:
                video_id = row['video_id']
                comments_response = get_comments(video_id, max_results=5)
                comment_list = [item.snippet.topLevelComment.snippet.textOriginal for item in comments_response.items]
                all_comments.extend(comment_list)
            except Exception as e:
                pass
                # print(f"Error fetching comments for video {video_id}: {e} Skipping this video.")
        text = " ".join(all_comments)

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    return wordcloud.to_image()
