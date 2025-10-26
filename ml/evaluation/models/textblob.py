from textblob import TextBlob

from evaluation.models.model import SentimentModel, Comment


class TextBlobModel(SentimentModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_sentiment(self, comments: list[Comment]) -> list[float]:
        result = []
        for comment in comments:
            blob = TextBlob(comment.comment)
            sentiments = [sentence.sentiment.polarity for sentence in blob.sentences]  # type: ignore
            result.append(sum(sentiments) / len(sentiments))
        return result


export_models = [TextBlobModel("textblob", "basic textblob")]
