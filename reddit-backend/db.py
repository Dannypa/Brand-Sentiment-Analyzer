import psycopg2
from models import PostCache
from datetime import datetime

def search_post_database(conn: psycopg2, query: str, startdate: datetime, enddate: datetime) -> list[PostCache]:
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM reddit_cache
                WHERE query = %s
                AND datetime >= %s
                AND datetime <= %s
            """, (query, startdate, enddate))
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
    except Exception as e:
        print(f"Error querying post database: {e}")
        return [] 
    return [PostCache(**dict(zip(columns, row))) for row in rows]
    
def insert_post_cache(conn: psycopg2, post_cache: list[PostCache]):
    with conn.cursor() as cur:
        try:
            cur.execute("""
                INSERT INTO reddit_cache (post_id, query, subreddit, datetime, title_sentiment, avg_comment_sentiment)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (post_id) DO NOTHING
            """, (
                post_cache.post_id,
                post_cache.query,
                post_cache.subreddit,
                post_cache.datetime,
                post_cache.title_sentiment,
                post_cache.avg_comment_sentiment
            ))
        except Exception as e:
            print(f"Error inserting video cache for post_id {post_cache.post_id}: {e}")
    conn.commit()
    return
