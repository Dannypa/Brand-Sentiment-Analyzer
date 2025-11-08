from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

api = FastAPI()


# protocols = ["http://", "https://"]
# ports = [":8080"]
# hosts = ["yt", "reddit"]
# allowed_origins = [
#     f"{protocol}{host}{port}"
#     for port in ports
#     for protocol in protocols
#     for host in hosts
# ]

# print(allowed_origins)

# api.add_middleware(
#     CORSMiddleware,
#     allow_origins=allowed_origins,
#     allow_methods=["*"],
# )


class Team(BaseModel):
    brand: Optional[str] = None
    title: Optional[str] = None
    topic: Optional[str] = None
    texts: list[str]


class SentimentQuery(BaseModel):
    teams: list[Team]


class SentimentResponse(BaseModel):
    sentiment: list[list[float]] = Field(
        ...,
        title="The sentiments of the texts; a list of lists of floating point numbers from -1 to 1.",
    )

    method: str


analyzer = SentimentIntensityAnalyzer()


def process_team_vader(team: Team) -> list[float]:
    # todo: split each text into sentences
    result = []
    for text in team.texts:
        result.append(analyzer.polarity_scores(text)["compound"])
    return result


@api.post("/get_sentiment")
def get_sentiment(query: SentimentQuery) -> SentimentResponse:
    result = [process_team_vader(team) for team in query.teams]
    return SentimentResponse(sentiment=result, method="vader")
