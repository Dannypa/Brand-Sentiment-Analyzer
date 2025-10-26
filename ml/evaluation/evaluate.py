from evaluation.models.model import Comment, SentimentModel
from pydantic import BaseModel
import pathlib
import json
from typing import Callable
from sklearn.metrics import mean_squared_error, accuracy_score
from time import perf_counter

### models
from evaluation.models.gemini import export_models as gemini_models
from evaluation.models.ollama import export_models as ollama_models
from evaluation.models.vader import export_models as vader_models
from evaluation.models.textblob import export_models as textblob_models
from evaluation.models.hf import export_models as hf_models

models: list[SentimentModel] = []
models.extend(vader_models)
models.extend(textblob_models)
models.extend(hf_models)
models.extend(gemini_models)
models.extend(ollama_models)

class ScoredComment(BaseModel):
    comment: Comment
    score: float | int


def load_data(
    path: (
        pathlib.Path | str
    ) = "/home/dannypa/aalto/ds-project-2025/repo/ml/evaluation/data.jsonl",
) -> list[ScoredComment]:
    result = []
    with open(path, "r") as fin:
        for line in fin:
            try:
                parsed = json.loads(line)
                score = parsed["score"]
                parsed.pop("score")
                comment = Comment(**parsed)
                result.append(ScoredComment(comment=comment, score=score))

            except ValueError as e:
                print("\n\n" + '=' * 10)
                print("Json parsing error!")
                print(e)
                print(line)
                print("\n\n" + '=' * 10)
                continue
    return result


def score_to_category(x: float) -> int:
    if x < -0.75:
        return -2
    elif -0.75 <= x < -0.25:
        return -1
    elif -0.25 <= x < 0.25:
        return 0
    elif 0.25 <= x < 0.75:
        return 1
    else:
        return 2
    

def score_to_binary(x: float) -> int:
    if x < 0:
        return -1
    elif x == 0:
        return 0
    else:
        return 1

def to_array(func: Callable[[float], float | int]) -> Callable[[list[float]], list[float | int]]:
    def inner(array: list[float]):
        return [func(x) for x in array]

    return inner


class Transformation(BaseModel):
    name: str
    transform: Callable[[list[float]], list[float | int]]
    loss_function: Callable[[list[float | int], list[float | int]], float]

transformations = [
    Transformation(
        name="Contiunous",
        transform=lambda x: x,
        loss_function=mean_squared_error
    ),
    Transformation(
        name="5 categories",
        transform=to_array(score_to_category),
        loss_function=accuracy_score
    ),
    Transformation(
        name="Binary",
        transform=to_array(score_to_binary),
        loss_function=accuracy_score
    )
]

UNDEF = -1

class ModelEvalResult(BaseModel):
    model_name: str
    scores: dict = dict()
    time_total: float = UNDEF
    time_per_comment: float = UNDEF
    token_total: int | None = None
    token_per_comment: float | None = None


def eval_model(model: SentimentModel, data: list[Comment], true_scores: list[float]) -> ModelEvalResult | None:
    print(f"Evaluating model {model.name}...")

    result = ModelEvalResult(model_name=model.name)
    try:
        start = perf_counter()
        base = model.get_sentiment(data)
        end = perf_counter()
    except Exception as e:
        print(e)
        print("Batch processing has failed! Trying one by one...")
        try:
            start = perf_counter()
            base = model.get_sentiment_one_by_one(data)
            end = perf_counter()
        except Exception as e:
            print(e)
            print("One by one procesing has also failed. Skipping...")
            return None

    result.time_total = end - start
    result.time_per_comment = (end - start) / len(data)
    
    if hasattr(model, "token_use"):
        result.token_total = model.token_use
        result.token_per_comment = model.token_use / len(data)
    # print(f"Took {round(end - start, 3)}s in total. {round(end - start) / len(data), 3} per comment.")
    
    
    for transformation in transformations:
        # print(f"{transformation.name}: ", end='')
        predictions = transformation.transform(base)
        actual = transformation.transform(true_scores)
        result.scores[transformation.name] = transformation.loss_function(predictions, actual)
        # print(transformation.loss_function(predictions, actual)) 
    return result


def get_column_width(column: str, header: str, rows: list[ModelEvalResult]) -> int:
     width = len(header)
     for row in rows:
         value = getattr(row, column)
         if isinstance(value, float):
             value = round(value, 3)
         width = max(width, len(str(value)))
     return width

def print_results(results: list[ModelEvalResult]):
    for result in results:
        print(result.time_per_comment, result.time_total)
    def get_display_value(result: ModelEvalResult, attr: str) -> str:
        if '.' in attr:  # nested attributes like scores.Binary
            parts = attr.split('.')
            value = getattr(result, parts[0]).get(parts[1], None)
        else:
            value = getattr(result, attr)

        if value == UNDEF or value is None:
            display_value = "N/A"
        elif isinstance(value, float):
            display_value = f"{value:.3f}"
        else:
            display_value = str(value)[:30]
        return display_value


    if not results:
        print("No results to display.")
        return
    
    columns = [
        ("Model", "model_name"),
        ("Time (s)", "time_total"), 
        ("Time/Comment (s)", "time_per_comment"),
        ("Tokens", "token_total"),
        ("Tokens/Comment", "token_per_comment")
    ]
    
    score_columns = []
    for transformation_name in results[0].scores.keys():
        score_columns.append((transformation_name, f"scores.{transformation_name}"))

    all_columns = columns + score_columns
    
    # calculate column widths
    col_widths = {}
    for header, attr in all_columns:
        width = len(header)
        for result in results:
           
            width = max(width, len(get_display_value(result, attr)))
        
        col_widths[header] = width + 2  # some padding
    
    # print header
    header_row = ""
    separator_row = ""
    for header, _ in all_columns:
        header_row += f"{header:<{col_widths[header]}}"
        separator_row += "-" * col_widths[header]
    
    print(header_row)
    print(separator_row)
    
    # print rows
    for result in results:
        row = ""
        for header, attr in all_columns:
            display_value = get_display_value(result, attr)           
            row += f"{display_value:<{col_widths[header]}}"
        print(row)


def main():
    data = load_data()
    unlabeled = [c.comment for c in data]
    true_scores = [c.score for c in data] 
    
    results: list[ModelEvalResult] = []
    for model in models:
        if (res := eval_model(model, unlabeled, true_scores)) is not None:
            results.append(res)

    print_results(results)

if __name__ == "__main__":
    main()
