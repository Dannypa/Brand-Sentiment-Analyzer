from pydantic import BaseModel, RootModel
from typing import Dict, Optional
from datetime import datetime

# Models for video search
class id(BaseModel):
    kind: str
    videoId: str
    channelId: Optional[str] = None
    playlistId: Optional[str] = None

class thumbnail(BaseModel):
    url: str
    width: int
    height: int

class thumbnails(BaseModel):
    default: thumbnail
    medium: thumbnail
    high: thumbnail
    standard: Optional[thumbnail] = None
    maxres: Optional[thumbnail] = None
                 
class searchSnippet(BaseModel):
    publishedAt: datetime
    channelId: str
    title: str
    description: str
    thumbnails: thumbnails
    channelTitle: str
    liveBroadcastContent: str

class searchItem(BaseModel):
    kind: str
    etag: str
    id: id
    snippet: searchSnippet
    channelTitle: Optional[str] = None
    liveBroadcastContent: Optional[str] = None

class searchListResponse(BaseModel):
    kind: str
    etag: str
    nextPageToken: Optional[str]
    prevPageToken: Optional[str] = None
    regionCode: str
    pageInfo: Dict[str, int]
    items: list[searchItem]

# Models for Comments
class commentSnippet(BaseModel):
    authorDisplayName: str
    authorProfileImageUrl: str
    authorChannelUrl: str
    authorChannelId: Dict[str, str]
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

class comment(BaseModel):
    kind: str
    etag: str
    id: str
    snippet: commentSnippet

class commentThreadSnippet(BaseModel):
    channelId: str
    videoId: str
    topLevelComment: comment
    canReply: bool
    totalReplyCount: int
    isPublic: bool

class commentThread(BaseModel):
    kind: str
    etag: str
    id: str
    snippet: commentThreadSnippet
    replies: Optional[Dict[str, list[comment]]] = None

class commentListResponse(BaseModel):
    kind: str
    etag: str
    nextPageToken: Optional[str]
    pageInfo: Dict[str, int]
    items: list[commentThread]

#Video models

class videoStatistics(BaseModel):
    viewCount: str
    likeCount: Optional[str] = None
    dislikeCount: Optional[str] = None
    favoriteCount: str
    commentCount: Optional[str] = None

class video(BaseModel):
    kind: str
    etag: str
    id: str
    statistics: videoStatistics

class pageInfo(BaseModel):
    totalResults: int
    resultsPerPage: int

class videoListResponse(BaseModel):
    kind: str
    etag: str
    pageInfo: pageInfo
    items: list[video]
    




