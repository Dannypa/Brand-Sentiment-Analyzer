from google import genai
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel
import json
import tqdm

from evaluation.models.model import SentimentModel, Comment
from evaluation.models.prompts import *


class SentimentResponse(BaseModel):
    sentiment: float


load_dotenv()
client = genai.Client()


class GeminiModel(SentimentModel):

    def __init__(
        self,
        *args,
        batch_size: int = 10,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.batch_size = batch_size
        self.system_prompt = system_prompt
        self.token_use = 0

    def get_sentiment(self, comments: list[Comment]) -> list[float]:
        result = []
        for i in tqdm.trange(0, len(comments), self.batch_size):
            # get data
            batch = comments[i : i + self.batch_size]
            objects = [c.model_dump() for c in batch]
            json_objects = json.dumps(objects)

            # query model
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=json_objects,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_prompt,
                    response_mime_type="application/json",
                    response_schema=list[SentimentResponse],
                ),
            )
            self.token_use += response.usage_metadata["total_token_count"]

            # process the predictions
            try:
                predictions = [p.sentiment for p in response.parsed]
                assert len(predictions) == min(self.batch_size, len(comments) - i)
            except Exception as e:
                print(f"Warning: error in gemini (parsed is none?): {e}")
                predictions = [0 for _ in range(self.batch_size)]

            result.extend(predictions)

        return result

    def get_token_use(self) -> int:
        return self.token_use


export_models = [GeminiModel("Gemini 2.0 flash lite", "default gemini model")]
