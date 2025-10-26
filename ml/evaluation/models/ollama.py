from evaluation.models.model import SentimentModel, Comment
from evaluation.models.prompts import *
import json
import requests
import tqdm


class OllamaModel(SentimentModel):

    def __init__(
        self,
        model_id: str,
        model_name: str | None = None,
        batch_size: int = 10,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        **kwargs,
    ):
        if model_name is None:
            model_name = model_id
        super().__init__(model_name, **kwargs)
        self.model_id = model_id
        self.batch_size = batch_size
        self.system_prompt = system_prompt

    def get_sentiment(self, comments: list[Comment]) -> list[float]:
        result = []
        for i in tqdm.trange(0, len(comments), self.batch_size):
            # get data
            batch = comments[i : i + self.batch_size]
            objects = [c.model_dump() for c in batch]
            json_objects = json.dumps(objects)

            # query model
            res = requests.post(
                "http://localhost:11434/api/generate",
                data=json.dumps({
                    "model": self.model_id,
                    "stream": False,
                    "system": DEFAULT_SYSTEM_PROMPT,
                    "prompt": json_objects,
                    "format": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "sentiment": {
                                    "type": "number",    
                                },
                            },
                            "required": [
                                "sentiment"
                            ]
                        }
                    }
                })
            )

            response = json.loads(res.json()["response"])
           

# process the predictions
            try:
                predictions = [p["sentiment"] for p in response]
                assert len(predictions) == min(self.batch_size, len(comments) - i)
            except Exception as e:
                print(f"Warning: error in {self.model_id} (parsed is none?): {e}")
                predictions = [0 for _ in range(self.batch_size)]

            result.extend(predictions)

        return result


export_models = [
    OllamaModel("gemma3:1b"),
    OllamaModel("gemma3:4b")
]
