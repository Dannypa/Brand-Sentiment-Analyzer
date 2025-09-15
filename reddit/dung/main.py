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

all = reddit.subreddit("all") # all subreddits

submissions = [submission for submission in all.search("nike", time_filter="month")]

print(f"Found {len(submissions)} submissions")

for submission in submissions:
    print(submission.title)
    print(submission.created_utc)
    print(submission.score)
    print()