from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from evaluation.models.model import SentimentModel, Comment


class VaderModel(SentimentModel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = SentimentIntensityAnalyzer()

    def get_sentiment(self, comments: list[Comment]) -> list[float]:
        result = []
        for comment in comments:
            result.append(self.model.polarity_scores(comment.comment)["compound"])
        return result


export_models = [VaderModel("Vader", "vader simple vader")]
