import psycopg2
from datetime import datetime
from models import VideoCache

def search_video_database(conn: psycopg2, query: str, startdate: datetime, enddate: datetime) -> list[VideoCache]:
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM youtube_cache
                WHERE query = %s
                AND datetime >= %s
                AND datetime <= %s
            """, (query, startdate, enddate))
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
    except Exception as e:
        print(f"Error querying video database: {e}")
        return [] 
    return [VideoCache(**dict(zip(columns, row))) for row in rows]
    
def insert_video_cache(conn: psycopg2, video_cache: list[VideoCache]):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO youtube_cache (video_id, query, datetime, views, likes, comments, avg_comment_sentiment, title_sentiment)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (video_id) DO NOTHING
            """, (
                video_cache.video_id,
                video_cache.query,
                video_cache.datetime,
                video_cache.views,
                video_cache.likes,
                video_cache.comments,
                video_cache.avg_comment_sentiment,
                video_cache.title_sentiment
            ))
        except Exception as e:
            print(f"Error inserting video cache for video_id {video_cache.video_id}: {e}")
    conn.commit()
    return


    
