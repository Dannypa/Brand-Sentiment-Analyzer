import asyncio
from re import A

import numpy as np
import pandas as pd
from PIL import Image
from wordcloud import WordCloud

from services import (
    remove_videos_without_brand_title,
    remove_videos_without_comments,
    video_to_dataframe,
)
from ytapi import get_comments_async, search_videos_async


async def process_row(row) -> list[str]:
    # print("a")
    try:
        # print("b")
        video_id = row["video_id"]
        # print("c")
        comments_response = await get_comments_async(video_id, max_results=5)
        # print("d")
        # print(comments_response)
        comment_list = [
            item.snippet.topLevelComment.snippet.textOriginal
            for item in comments_response.items
        ]
        return comment_list
    except Exception as e:
        # print(e)
        return []
        # print(f"Error fetching comments for video {video_id}: {e} Skipping this video.")


async def word_cloud(brands: list[str]) -> Image:
    text = "test"
    for brand in brands:
        search_response = await search_videos_async(f"{brand} bad", max_results=5)

        videos_df = await video_to_dataframe(search_response)
        videos_df = remove_videos_without_comments(videos_df)
        videos_df = remove_videos_without_brand_title(videos_df, brand)
        print(videos_df)
        all_comments = []

        tasks = [process_row(row) for _, row in videos_df.iterrows()]
        for res in await asyncio.gather(*tasks):
            print(res)
            if isinstance(res, list):
                all_comments.extend(res)

        text = " ".join(all_comments).lower()

    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(
        text
    )
    return wordcloud.to_image()
