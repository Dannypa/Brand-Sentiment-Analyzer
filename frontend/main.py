from dash import Dash, html, dcc
import requests
import os
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import json

load_dotenv()


# class AddressConfig(BaseModel):
#     host: str
#     port: Optional[int]
#     protocol: str

#     def __init__(
#         self,
#         prefix: str,
#         d_host: str = "0.0.0.0",
#         d_port: Optional[int] = 8080,
#         d_protocol: str = "http://",
#     ):
#         self.host = os.environ.get(f"{prefix}HOST", d_host)
#         env_port = os.environ.get(f"{prefix}PORT")
#         if env_port is not None:
#             self.port = int(env_port)
#         else:
#             self.port = d_port
#         self.protocol = os.environ.get(f"{prefix}PROTOCOL", d_protocol)

#     def build_url(self) -> str:
#         port = "" if self.port is None else f":{self.port}"
#         return f"{self.protocol}{self.host}{port}"


# frontend_config = AddressConfig("")
# yt_url = AddressConfig("YT", d_host="yt", d_port=8080).build_url() + "/charts"
# reddit_url = AddressConfig("REDDIT", d_host="reddit", d_port=8080).build_url() + "/charts"


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = os.environ.get("PORT", 8080)
yt_url = os.environ.get("YT_URL", "http://yt:8080/charts")
reddit_url = os.environ.get("REDDIT_URL", "http://reddit:8080/charts")

def construct_chart(url: str) -> list[dcc.Graph | html.Div]:
    try:
        data = requests.get(f"{url}?brand=\"nike\"").json()
    except Exception as e:
        print(e)
        return [html.Div(
            children="The data was supposed to be here, but we didn't get it. womp womp."
        )]
    result = []
    for obj in data:
        result.append(dcc.Graph(figure=obj["plotly_json"]))
    return result


app = Dash()

app.layout = [
    html.Div(children="Hello World"),
    html.Hr(),
    html.Div(children=construct_chart(yt_url)),
    html.Hr(),
    html.Div(construct_chart(reddit_url)),
]

if __name__ == "__main__":
    app.run(debug=True, host=HOST, port=PORT)

