from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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
    nextPageToken: Optional[str]
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
    nextPageToken: Optional[str]
    pageInfo: dict[str, int]
    items: list[CommentThread]


# Video models

class VideoStatistics(BaseModel):
    viewCount: str
    likeCount: Optional[str] = None
    dislikeCount: Optional[str] = None
    favoriteCount: str
    commentCount: Optional[str] = None


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
