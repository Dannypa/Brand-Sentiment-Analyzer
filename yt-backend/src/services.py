from ytapi import get_video_details, get_comments, search_videos
from models import CommentListResponse, SearchListResponse, VideoListResponse, VideoCache
import pandas as pd
from ml import get_sentiment
import psycopg2
from db import search_video_database, insert_video_cache
from datetime import datetime
import datetime as dt

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

def split_date_range(start_date: datetime, end_date: datetime, n: int) -> list[tuple[datetime, datetime]]:
    time_difference = end_date - start_date
    print(type(time_difference))
    num_days = time_difference.days

    if n > num_days:
        n = num_days

    interval_delta = int(time_difference.days) / n
    intervals = []
    current_date = start_date

    for _ in range(n-1):
        next_date = current_date + dt.timedelta(days=interval_delta)
        intervals.append((current_date, next_date))
        current_date = next_date
    intervals.append((current_date, end_date))

    return intervals

def get_all_video_data(conn: psycopg2, query: str, max_results: int, start: datetime, end: datetime) -> list[VideoCache]:

    video_data = search_video_database(conn, query, start, end)
    print(f"Found {len(video_data)} results")

    if len(video_data) < max_results:
        if max_results > 50:
            iterations = (max_results // 50) + 1
            try:
                intervals = split_date_range(start, end, iterations)
            except Exception as e:
                print(f"Error splitting date range: {e}")
                intervals = [(start, end)]
        else:
            intervals = [(start, end)]

        video_data = []
        for (start_date, end_date) in intervals:
            videos = search_videos(query, max_results=50, start_date=start_date, end_date=end_date)
            
            for item in videos.items:

                video_id = item.id.videoId
                try:
                    video_details = get_video_details(video_id)
                    video_details = VideoListResponse(**video_details)
                    video_stats = get_video_stats(video_details)

                    if video_stats.commentCount is None or video_stats.commentCount == 0:
                        continue
                    comments = get_comments(video_id)
                    top_comments = comments_to_list_of_top_level(comments)
                    comment_count = video_stats.commentCount or 0
                    like_count = video_stats.likeCount or 0
                    comments_sentiments = get_sentiment(top_comments)

                    if not comments_sentiments or len(comments_sentiments) == 0:
                        continue

                    avg_comment_sentiment = sum(comments_sentiments) / len(comments_sentiments) if len(comments_sentiments) != 0 else 0
                    title_sentiment = get_sentiment([item.snippet.title])[0] or 0.0
                    avg_sentiment = (avg_comment_sentiment + title_sentiment) / 2
                    weighted_sentiment = (avg_comment_sentiment * comment_count * 0.988) + (title_sentiment * like_count * 0.012)
                    video_data.append(VideoCache(
                        video_id=video_id,
                        query=query,
                        datetime=item.snippet.publishedAt,
                        views=video_stats.viewCount or 0,
                        likes=video_stats.likeCount,
                        comments=video_stats.commentCount,
                        avg_comment_sentiment=avg_comment_sentiment,
                        title_sentiment=title_sentiment,
                        avg_sentiment=avg_sentiment,
                        weighted_sentiment=weighted_sentiment
                    ))
                except Exception as e:
                    print(f"Error processing video ID {video_id}: {e}")
                    continue
            print(f"Inserting {len(video_data)} new video records into the database...")
        for video in video_data:
            try:
                insert_video_cache(conn, video)
            except Exception as e:
                pass
                print(f"Error inserting video cache for video_id {video.video_id}: {e}")

    return video_data