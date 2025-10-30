from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Model for charts
class Chart(BaseModel):
    title: Optional[str]
    plotly_json: str

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

