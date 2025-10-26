from ytapi import execute_search_query_pydantic, execute_comment_query_pydantic
from models import *
from dataclasses import dataclass
from random import shuffle
import os
import json

@dataclass
class SampleVideo:
    title: str
    brand: str
    comments: list[str]


def get_comments(video_id: str, lim: int = 20) -> list[str]:
    comments = execute_comment_query_pydantic(CommentThreadRetrieveQuery(video_id=video_id, max_results=lim))
    result = []
    for item in comments.items:
        result.append(item.snippet.topLevelComment.snippet.textOriginal)

    return result


def add_videos_about_brand(brand: str, result: list, lim: int = 66):
    videos = execute_search_query_pydantic(SearchQuery(q=brand))

    current_count = 0
    for item in videos.items:
        title = item.snippet.title
        try:
            comments = get_comments(item.id.videoId, lim=lim // 5)
        except ValueError as e:
            print(f"Something went wrong for video {title}. Error: {e}")
            continue

        result.append(SampleVideo(
            title=title,
            comments=comments,
            brand=brand
        ))
        current_count += len(comments)
        if current_count >= lim: 
            break


def main():
    sample = []
    
    add_videos_about_brand("nike", sample)
    add_videos_about_brand("shein", sample)
    add_videos_about_brand("adidas", sample)
    shuffle(sample)

    output_path = os.environ.get("SAMPLE_DOWNLOAD_OUTPUT", "sample/sample.json")
    
    comments = []
    for video in sample:
        for comment in video.comments:
            comments.append({
                "comment": comment,
                "title": video.title,
                "brand": video.brand,
            })
    
    print(f"In total {len(comments)} comments.")

    with open(output_path, 'w') as f:
        json.dump(comments, f)
        
if __name__ == "__main__":
    main()

