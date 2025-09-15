from dotenv import load_dotenv
import praw
import os
from transformers import pipeline

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

# list_of_topics = ["climate", "sustainability", "diversity", "inclusion", "equity"] 
def sentiment_on_topic(brand, topic):
    pass

def attention(brand):
    pass

sentiment_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")

def sentiment(brand) -> float:
    submissions = [submission for submission in all.search(brand, time_filter="month")]
    # print(f"Found {len(submissions)} submissions")
    sentiments = [sentiment_pipeline(submission.title) for submission in submissions]
    
    # # print 5 sample sentiments
    # for i in range(min(5, len(sentiments))):
    #     print(f"Title: {submissions[i].title}")
    #     print(f"Sentiment: {sentiments[i]}")

    score = 0.0
    for sentiment in sentiments:
        if sentiment[0]['label'] == 'POS':
            score += sentiment[0]['score']
        elif sentiment[0]['label'] == 'NEG':
            score -= sentiment[0]['score']
    
    return (score / len(submissions)) if len(submissions) > 0 else 0.0

list_of_brands = ["nike", "adidas", "puma", "reebok", "new balance"]

for brand in list_of_brands:
    print(f"Sentiment for {brand}: {sentiment(brand)}")