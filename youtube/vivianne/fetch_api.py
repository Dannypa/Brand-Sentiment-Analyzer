from youtube.api import *
from youtube.models import *
import pandas as pd
from datetime import datetime, timedelta, timezone

def time_period(d: int):
    today = datetime.now(timezone.utc)
    today_str = today.strftime("%Y-%m-%dT%H:%M:%SZ")
    thirty_days_ago = today - timedelta(days=d)
    thirty_days_ago_str = thirty_days_ago.strftime("%Y-%m-%dT%H:%M:%SZ")
    return today, thirty_days_ago

def fetch_videos(brand: str, days: int, pages: int = 1):
    today, thirty_days_ago = time_period(days)
    q = f"{brand.lower()} bad"
    page_token = None
    brand_videos = []
    for i in range(pages):
        query = SearchQuery(
            q=q,
            max_results=50,
            published_after=thirty_days_ago,
            published_before=today,
            page_token=page_token
        )
        try: 
            videos = execute_search_query(query)
        except Exception as e: 
            print(e)
            break
        try: 
            videos = SearchListResponse(**videos)
        except Exception as e: 
            print(e)
            continue

        brand_videos.extend(videos.items)
        page_token = videos.nextPageToken
        if not page_token:
            break

    print(f"Fetched {len(brand_videos)} videos for {brand}.")
    return brand_videos 

def fetch_comments(video_id: str, brand: str, sent_ana, max_comments: int = 50):
    all_comments = []
    all_comment_scores = []
    count = 0
    page_token = None
    while count < max_comments: 
        try:
            vid_comments = get_comments(video_id, max_results=50)
            vid_comments = CommentListResponse(**vid_comments)
        except Exception as e:
            print(f"Skipping comments for {video_id}: {e}")
            break

        for c in vid_comments.items:
            if count >= max_comments: 
                break
            comment = c.snippet.topLevelComment.snippet
            sent_score = sent_ana.polarity_scores(comment.textOriginal)["compound"]
            all_comment_scores.append(sent_score)
            comment_data = {
                "video_id": c.snippet.videoId,
                "brand": brand,
                "publishedAt": comment.publishedAt,
                "comment_id": c.snippet.topLevelComment.id,
                "top_level_id": None,
                "text": comment.textOriginal,
                "sentiment": sent_score
            }
            all_comments.append(comment_data)
            count +=1 

            if c.replies:
                for reply in c.replies.get("comments", []):
                    if count >= max_comments: 
                        break
                    r_score = sent_ana.polarity_scores(reply.snippet.textOriginal)["compound"]
                    all_comment_scores.append(r_score)
                    r_data = {
                        "video_id": c.snippet.videoId,
                        "brand": brand,
                        "publishedAt": reply.snippet.publishedAt,
                        "comment_id": reply.id,
                        "top_level_id": reply.snippet.parentId,
                        "text": reply.snippet.textOriginal,
                        "sentiment": r_score
                    }
                    all_comments.append(r_data)
                    count += 1

        if count >= max_comments or not page_token:
            break
    avg_score = sum(all_comment_scores) / len(all_comment_scores) if all_comment_scores else 0
    return all_comments, avg_score

def process_video(vid, brand: str, sent_ana, max_comments: int = 100):
    video_id = vid.id.videoId
    video_title = vid.snippet.title
    video_publish = vid.snippet.publishedAt

    details = get_video_details(video_id)
    details = VideoListResponse(**details)
    stats = details.items[0].statistics

    views = int(stats.viewCount or 0)
    likes = int(stats.likeCount or 0)
    comments_count = int(stats.commentCount or 0)

    comments, avg_comment_sent = fetch_comments(video_id, brand, sent_ana, max_comments)
    title_sent = sent_ana.polarity_scores(str(video_title))["compound"]

    w_likes = 0.012 
    w_comments = 0.988
    total_sent = title_sent * likes * w_likes + avg_comment_sent * comments_count * w_comments

    video_data = {
    "video_id": video_id,
    "video_title": video_title,
    "brand": brand,
    "publishedAt": video_publish,
    "views": views,
    "likes": likes,
    "comments": comments_count,
    "sentiment_comments": avg_comment_sent,
    "sentiment_video": title_sent,
    "total_sentiment": total_sent
    }

    return video_data, comments
                
def scale_results(video_df: pd.DataFrame):
    min_sent = video_df["total_sentiment"].min()
    max_sent = video_df["total_sentiment"].max()

    if min_sent == max_sent:
        video_df["scaled_result"] = 0
    else:
        video_df["scaled_result"] = video_df["total_sentiment"]/max(abs(min_sent), abs(max_sent))

    return video_df, min_sent, max_sent
