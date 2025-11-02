import requests

address = "http://ml:8080/get_sentiment"

def get_sentiment(texts: list[str]) -> list[float]:
    data = {"teams": [{"texts": texts}]}
    sentiment = requests.post(address, json=data, headers={"Content-Type": "application/json"}).json()['sentiment']
    return sentiment[0]


def draft():
    print(get_sentiment(["i hate nn"]))

if __name__ == "__main__":
    draft()

