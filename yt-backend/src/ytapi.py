import os
import dotenv
import requests
from models import (
    SearchListResponse,
    VideoListResponse,
    SearchQuery,
    CommentThreadRetrieveQuery,
    CommentListResponse
)

dotenv.load_dotenv()

key = os.getenv("YOUTUBE_KEY")
# Video search-related functions
def query_youtube_api(url: str) -> dict:
    resp = requests.get(
        url,
        headers={"Accept": "application/json"},
    )
    if resp.status_code != 200:
        raise ValueError(f"Request to the api failed. Code {resp.status_code}. Error: {resp.text}")
    return resp.json()


def execute_search_query(
        q: SearchQuery,
) -> dict:
    query = [
        "https://youtube.googleapis.com/youtube/v3/search?",
        f"q={q.q}&",
        f"part={','.join(q.part)}&",
        f"type={q.type}&",
        f"maxResults={q.max_results}&",
    ]

    rfc3339_format = "%Y-%m-%dT%H:%M:%SZ"
    if q.published_after is not None:
        query.append(f"publishedAfter={q.published_after.strftime(rfc3339_format)}&")
    if q.published_before is not None:
        query.append(f"publishedBefore={q.published_before.strftime(rfc3339_format)}&")

    query.append(f"videoDuration={','.join(q.video_duration)}&")
    query.append(f"order={q.order}&")
    query.append(f"relevanceLanguage={q.language}&")
    if q.page_token is not None:
        query.append(f"pageToken={q.page_token}&")
    query.append(f"key={key}")

    return query_youtube_api(''.join(query))


def execute_search_query_pydantic(q: SearchQuery) -> SearchListResponse:
    return SearchListResponse(**execute_search_query(q))


def search_videos(query, max_results=50, start_date=None, end_date=None) -> SearchListResponse:
    return execute_search_query_pydantic(
        SearchQuery(q=query, max_results=max_results, published_after=start_date, published_before=end_date)
    )

# Comment-related functions
def execute_comment_query(
        q: CommentThreadRetrieveQuery
):
    query = [
        "https://youtube.googleapis.com/youtube/v3/commentThreads?",
        f"videoId={q.video_id}&",
        f"part={','.join(q.part)}&",
        f"textFormat=plainText&",
        f"maxResults={q.max_results}&",
        f"order={q.order}&",
    ]
    if q.search_terms is not None:
        query.append(f"searchTerms={q.search_terms}&")
    if q.page_token is not None:
        query.append(f"pageToken={q.page_token}&")
    query.append(f"key={key}")

    return query_youtube_api(''.join(query))


def execute_comment_query_pydantic(q: CommentThreadRetrieveQuery) -> CommentListResponse:
    return CommentListResponse(**execute_comment_query(q))


def get_comments(video_id, max_results=50) -> CommentListResponse:
    return execute_comment_query_pydantic(CommentThreadRetrieveQuery(video_id=video_id, max_results=max_results))


# Video details-related functions
def execute_video_query(video_id: str):
    query = [
        "https://www.googleapis.com/youtube/v3/videos?",
        f"id={video_id}&",
        f"part=statistics&",
        f"key={key}"
    ]
    return query_youtube_api(''.join(query))


def execute_video_query_pydantic(video_id: str):
    return VideoListResponse(**execute_video_query(video_id))


def get_video_details(video_id: str):
    return execute_video_query(video_id)
