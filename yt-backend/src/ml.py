import asyncio

import aiohttp

address = "http://ml:8080/get_sentiment"


async def get_sentiment(texts: list[str]) -> list[float]:
    data = {"teams": [{"texts": texts}]}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            address, json=data, headers={"Content-Type": "application/json"}
        ) as resp:
            sentiment = (await resp.json())["sentiment"]
    return sentiment[0]


def draft():
    print(asyncio.run(get_sentiment(["i hate nn"])))


if __name__ == "__main__":
    draft()
