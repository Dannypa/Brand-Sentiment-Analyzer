import asyncio
import os
import time

import aiohttp
import dotenv
import requests

from models import (
    CommentListResponse,
    CommentThreadRetrieveQuery,
    SearchListResponse,
    SearchQuery,
    VideoListResponse,
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
        print(f"Error response from YouTube API: {resp.status_code} - {resp.text}")
        raise ValueError(
            f"Request to the api failed. Code {resp.status_code}. Error: {resp.text}"
        )
    return resp.json()


last_requests: list[float] = []
queue = []


def relax_last():
    while len(last_requests) > 0 and time.perf_counter() - last_requests[0] > 1:
        last_requests.pop(0)


async def query_youtube_api_async(url: str) -> dict:
    queue.append(url)
    relax_last()
    while len(last_requests) > 100:
        await asyncio.sleep(0.5)
        relax_last()
    url = queue.pop(0)
    last_requests.append(time.perf_counter())
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Accept": "application/json"}) as resp:
            if resp.status != 200:
                print(f"Error response from YouTube API: {resp.status} - {resp.text}")
                raise ValueError(
                    f"Request to the api failed. Code {resp.status}. Error: {resp.text}"
                )
            return await resp.json()


def check_key():
    if key is None:
        raise ValueError("API_KEY not provided!")


def execute_search_query(
    q: SearchQuery,
) -> dict:
    check_key()
    return query_youtube_api(q.to_str(key))


async def execute_search_query_async(q: SearchQuery) -> dict:
    check_key()
    return await query_youtube_api_async(q.to_str(key))


def execute_search_query_pydantic(q: SearchQuery) -> SearchListResponse:
    return SearchListResponse(**execute_search_query(q))


async def execute_search_query_pydantic_async(q: SearchQuery) -> SearchListResponse:
    return SearchListResponse(**(await execute_search_query_async(q)))


def search_videos(
    query, max_results=50, start_date=None, end_date=None
) -> SearchListResponse:
    return execute_search_query_pydantic(
        SearchQuery(
            q=query,
            max_results=max_results,
            published_after=start_date,
            published_before=end_date,
        )
    )


async def search_videos_async(
    query, max_results=50, start_date=None, end_date=None
) -> SearchListResponse:
    return await execute_search_query_pydantic_async(
        SearchQuery(
            q=query,
            max_results=max_results,
            published_after=start_date,
            published_before=end_date,
        )
    )


# Comment-related functions
def execute_comment_query(q: CommentThreadRetrieveQuery):
    check_key()
    return query_youtube_api(q.to_str(key))


async def execute_comment_query_async(q: CommentThreadRetrieveQuery):
    check_key()
    return await query_youtube_api_async(q.to_str(key))


def execute_comment_query_pydantic(
    q: CommentThreadRetrieveQuery,
) -> CommentListResponse:
    return CommentListResponse(**execute_comment_query(q))


async def execute_comment_query_pydantic_async(
    q: CommentThreadRetrieveQuery,
) -> CommentListResponse:
    return CommentListResponse(**(await execute_comment_query_async(q)))


def get_comments(video_id, max_results=50) -> CommentListResponse:
    return execute_comment_query_pydantic(
        CommentThreadRetrieveQuery(video_id=video_id, max_results=max_results)
    )


async def get_comments_async(video_id, max_results=50) -> CommentListResponse:
    return await execute_comment_query_pydantic_async(
        CommentThreadRetrieveQuery(video_id=video_id, max_results=max_results)
    )


# Video details-related functions


def get_video_query_str(video_id: str) -> str:
    query = [
        "https://www.googleapis.com/youtube/v3/videos?",
        f"id={video_id}&",
        f"part=statistics&",
        f"key={key}",
    ]
    return "".join(query)


def execute_video_query(video_id: str):
    return query_youtube_api(get_video_query_str(video_id))


def execute_video_query_pydantic(video_id: str):
    return VideoListResponse(**execute_video_query(video_id))


def get_video_details(video_id: str):
    return execute_video_query(video_id)


async def get_video_details_async(video_id: str):
    return VideoListResponse(
        **(await query_youtube_api_async(get_video_query_str(video_id)))
    )
