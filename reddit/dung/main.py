from dotenv import load_dotenv
import praw
import os

load_dotenv()

reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_APP_ID"),
    client_secret=os.getenv("REDDIT_APP_SECRET"),
    password=os.getenv("REDDIT_PASSWORD"),
    user_agent=f"testscript by u/{os.getenv('REDDIT_USERNAME')}",
    username=os.getenv("REDDIT_USERNAME"),
)

print(reddit.user.me())
