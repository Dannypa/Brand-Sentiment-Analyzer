from evaluation.models.model import SentimentModel, Comment
from transformers import pipeline


def sentiment_to_score(prediction: dict):
    coef = 0
    label = prediction["label"].lower()
    if label.startswith("neg"):
        coef = -1
    elif label.startswith("pos"):
        coef = 1
    return prediction["score"] * coef


class HfModel(SentimentModel):

    def __init__(self, model_id: str, description: str | None = None):
        if description is None:
            description = model_id
        super().__init__(name=model_id, description=description)
        self.model = pipeline("text-classification", model_id)

    def get_sentiment(self, comments: list[Comment]) -> list[float]:
        # print(list(comment.comment for comment in comments))
        # assert all(isinstance(comment.comment, str) for comment in comments) 
        sentiments = self.model(list(comment.comment for comment in comments))
        return [sentiment_to_score(p) for p in sentiments]


export_models = [
    HfModel("cardiffnlp/twitter-roberta-base-sentiment-latest"),
    HfModel("cardiffnlp/twitter-xlm-roberta-base-sentiment"),
    HfModel("nlptown/bert-base-multilingual-uncased-sentiment"),
    HfModel("lxyuan/distilbert-base-multilingual-cased-sentiments-student"),
]
