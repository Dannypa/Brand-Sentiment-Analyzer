from pydantic import BaseModel, JsonValue, Field
from typing import Optional
from datetime import datetime


# Model for building a search query
class SearchQuery(BaseModel):
    q: str
    part: tuple[str] = ("id", "snippet")
    type: str = "video"
    max_results: int = 50
    published_after: Optional[datetime] = None
    published_before: Optional[datetime] = None
    video_duration: tuple[str] = ("medium",)
    order: str = "relevance"
    language: str = "en"
    page_token: Optional[str] = None


class CommentThreadRetrieveQuery(BaseModel):
    video_id: str
    part: tuple[str] = ("snippet",)
    max_results: int = 100
    order: str = "relevance"
    search_terms: Optional[tuple[str]] = None
    page_token: Optional[str] = None


# Models for video search
class Id(BaseModel):
    kind: str
    videoId: str
    channelId: Optional[str] = None
    playlistId: Optional[str] = None


class Thumbnail(BaseModel):
    url: str
    width: int
    height: int


class Thumbnails(BaseModel):
    default: Thumbnail
    medium: Thumbnail
    high: Thumbnail
    standard: Optional[Thumbnail] = None
    maxres: Optional[Thumbnail] = None


class SearchSnippet(BaseModel):
    publishedAt: datetime
    channelId: str
    title: str
    description: str
    thumbnails: Thumbnails
    channelTitle: str
    liveBroadcastContent: str


class SearchItem(BaseModel):
    kind: str
    etag: str
    id: Id
    snippet: SearchSnippet
    channelTitle: Optional[str] = None
    liveBroadcastContent: Optional[str] = None


class SearchListResponse(BaseModel):
    kind: str
    etag: str
    nextPageToken: Optional[str] = None
    prevPageToken: Optional[str] = None
    regionCode: str
    pageInfo: dict[str, int]
    items: list[SearchItem]


# Models for Comments
class CommentSnippet(BaseModel):
    authorDisplayName: str
    authorProfileImageUrl: str
    authorChannelUrl: str
    authorChannelId: dict[str, str]
    channelId: str
    textDisplay: str
    textOriginal: str
    parentId: Optional[str] = None
    canRate: bool
    viewerRating: Optional[str] = None
    likeCount: int
    moderationStatus: Optional[str] = None
    publishedAt: datetime
    updatedAt: datetime


class Comment(BaseModel):
    kind: str
    etag: str
    id: str
    snippet: CommentSnippet


class CommentThreadSnippet(BaseModel):
    channelId: str
    videoId: str
    topLevelComment: Comment
    canReply: bool
    totalReplyCount: int
    isPublic: bool


class CommentThread(BaseModel):
    kind: str
    etag: str
    id: str
    snippet: CommentThreadSnippet
    replies: Optional[dict[str, list[Comment]]] = None


class CommentListResponse(BaseModel):
    kind: str
    etag: str
    nextPageToken: Optional[str] = None
    pageInfo: dict[str, int]
    items: list[CommentThread]


# Video models

class VideoStatistics(BaseModel):
    viewCount: int
    likeCount: Optional[int] = None
    dislikeCount: Optional[int] = None
    favoriteCount: int
    commentCount: Optional[int] = None


class Video(BaseModel):
    kind: str
    etag: str
    id: str
    statistics: VideoStatistics


class PageInfo(BaseModel):
    totalResults: int
    resultsPerPage: int


class VideoListResponse(BaseModel):
    kind: str
    etag: str
    pageInfo: PageInfo
    items: list[Video]


# Model for charts
class Chart(BaseModel):
    title: Optional[str]
    plotly_json: str # test json string

# Models for ML service
class Team(BaseModel):
    brand: Optional[str] = None
    title: Optional[str] = None
    topic: Optional[str] = None
    texts: list[str]

class SentimentQuery(BaseModel):
    teams: list[Team]

class SentimentResponse(BaseModel):
    sentiment: list[list[float]] = Field(..., title="The sentiments of the texts; a list of lists of floating point numbers from -1 to 1.")

