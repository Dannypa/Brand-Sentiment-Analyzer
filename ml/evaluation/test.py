from evaluation.models.model import Comment, SentimentModel
from evaluation.models.hf import export_models as hf_models
from evaluation.models.gemini import export_models as gemini_models
from evaluation.models.vader import export_models as vader_models
from evaluation.models.textblob import export_models as textblob_models
from evaluation.models.ollama import export_models as ollama_models


def test(models: list[SentimentModel]):
    print()
    print("=" * 10 + "STARTING TESTING" + "=" * 10)
    print()

    comments_text = [
        "I hate nike",
        "I like nike",
        "nike is alright",
        "nike is the worst company to ever exist",
        "nike is kinda goofy",
    ]

    comments = [
        Comment(title="", brand="nike", comment=comment) for comment in comments_text
    ]

    for model in models:
        print(model.name, end="  | ")
        print(model.get_sentiment(comments))

    print()
    print("=" * 10 + "FINISHED TESTING" + "=" * 10)
    print()


def main():
    models = []

    models.extend(textblob_models)
    models.extend(vader_models)
    models.extend(hf_models)
    models.extend(gemini_models)
    models.extend(ollama_models)

    test(models)


if __name__ == "__main__":
    main()
