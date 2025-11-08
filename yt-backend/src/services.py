from ytapi import get_video_details, get_comments, search_videos
from models import CommentListResponse, SearchListResponse, VideoListResponse, VideoCache
import pandas as pd
from ml import get_sentiment
import psycopg2
from db import search_video_database, insert_video_cache
from datetime import datetime

def get_comment_reply_dict(comment_threads: CommentListResponse):
    comment_reply_dict = {}
    for comment_thread in comment_threads.items:
        top_level_comment = comment_thread.snippet.topLevelComment
        comment_text = top_level_comment.snippet.textOriginal
        replies = comment_thread.replies['comments'] if comment_thread.replies else []
        reply_texts = []
        for reply in replies:
            reply_text = reply.snippet.textOriginal
            reply_texts.append(reply_text)
        comment_reply_dict[comment_text] = reply_texts
    return comment_reply_dict


def video_to_dataframe(videos: SearchListResponse, video_stats=None):
    video_data = []
    for item in videos.items:
        video_id = item.id.videoId
        video_details = get_video_details(video_id)
        video_details = VideoListResponse(**video_details)
        video_stats = get_video_stats(video_details)
        video_data.append({
            'video_id': video_id,
            'title': item.snippet.title,
            'description': item.snippet.description,
            'published_at': item.snippet.publishedAt,
            'channel_title': item.snippet.channelTitle,
            'like_count': video_stats.likeCount,
            'view_count': video_stats.viewCount,
            'comment_count': video_stats.commentCount,
        })
    df = pd.DataFrame(video_data)
    return df

def remove_videos_without_comments(videos_df: pd.DataFrame):
    filtered_df = videos_df[videos_df['comment_count'].notna() & (videos_df['comment_count'] > 0)]
    return filtered_df

def remove_videos_without_brand_title(videos_df: pd.DataFrame, brand_name: str):
    filtered_df = videos_df[videos_df['title'].str.contains(brand_name, case=False, na=False)]
    return filtered_df

def get_video_stats(video_details: VideoListResponse):
    stats = video_details.items[0].statistics
    return stats

def comments_to_list_of_top_level(comments: CommentListResponse):
    comment_list = []
    for item in comments.items:
        top_level_comment = item.snippet.topLevelComment
        comment_text = top_level_comment.snippet.textOriginal
        comment_list.append(comment_text)
    return comment_list


def get_all_video_data(conn: psycopg2, query: str, max_results: int, start_date: datetime, end_date: datetime) -> list[VideoCache]:
    
    video_data = search_video_database(conn, query, start_date, end_date)
    print(f"Found restulrts amount: {len(video_data)}")

    if len(video_data) < max_results:
        print("Fetching more data from YouTube API...")
        videos = search_videos(query, max_results=max_results, start_date=start_date, end_date=end_date)
        print(videos)
        video_data = []

        print(f"Processing {len(videos.items)} videos from YouTube API...")
        
        for item in videos.items:

            video_id = item.id.videoId
            print(f"Processing video ID: {video_id}")
            video_details = get_video_details(video_id)
            video_details = VideoListResponse(**video_details)
            video_stats = get_video_stats(video_details)
            
            if video_stats.commentCount is None or video_stats.commentCount == 0:
                print(f"Skipping video ID {video_id} due to no comments.")
                continue
            
            comments = get_comments(video_id)
            top_comments = comments_to_list_of_top_level(comments)
            comment_count = video_stats.commentCount
            like_count = video_stats.likeCount
            comments_sentiments = get_sentiment(top_comments)
            # Print each comment with its sentiment as a tuple
            if len(top_comments) != len(comments_sentiments):
                print("wth why is this happening?")
                print(top_comments)
                print(comments_sentiments)
            if not comments_sentiments or len(comments_sentiments) == 0:
                print(f"Skipping video ID {video_id} due to no comment sentiments.")
                continue

            avg_comment_sentiment = sum(comments_sentiments) / len(comments_sentiments) if len(comments_sentiments) != 0 else 0
            title_sentiment = get_sentiment([item.snippet.title])[0]
            avg_sentiment = (avg_comment_sentiment + title_sentiment) / 2
            weighted_sentiment = (avg_comment_sentiment * comment_count * 0.988) + (title_sentiment * like_count * 0.012)

            video_data.append(VideoCache(
                video_id=video_id,
                query=query,
                datetime=item.snippet.publishedAt,
                views=video_stats.viewCount,
                likes=video_stats.likeCount,
                comments=video_stats.commentCount,
                avg_comment_sentiment=avg_comment_sentiment,
                title_sentiment=title_sentiment,
                avg_sentiment=avg_sentiment,
                weighted_sentiment=weighted_sentiment
            ))
        print(f"Inserting {len(video_data)} new video records into the database...")
        for video in video_data:
            try:
                insert_video_cache(conn, video)
            except Exception as e:
                print(f"Error inserting video cache for video_id {video.video_id}: {e}")

    return video_data