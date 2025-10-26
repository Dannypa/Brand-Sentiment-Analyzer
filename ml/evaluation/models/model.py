from abc import ABC, abstractmethod
from pydantic import BaseModel


class Comment(BaseModel):
    title: str
    brand: str
    comment: str


class SentimentModel(ABC):
    def __init__(self, name: str, description: str | None = None):
        self.name = name
        self.description = description

    @abstractmethod
    def get_sentiment(self, comments: list[Comment]) -> list[float]:
        pass
    
    def get_sentiment_one_by_one(self, comments: list[Comment]) -> list[float]:
        result = []
        for comment in comments:
            try:
                sentiment = self.get_sentiment([comment])[0]
            except Exception as e:
                print(f"failed on {comment}: {e}")
                print("defaulting to 0...")
                sentiment = 0
            result.append(sentiment)
        return result
