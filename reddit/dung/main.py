import math
import praw
import os
from transformers import pipeline
from dotenv import load_dotenv
import matplotlib.pyplot as plt

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
sentiment_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")

def get_submissions(query, time_filter="month"):
    return [submission for submission in all.search(query, time_filter=time_filter)]

def single_score(result) -> float:
    """
    Convert the sentiment analysis result into a single score.
    POS -> +1, NEG -> -1, NEU -> 0
    
    This could maybe be done better 
    """
    score = result['POS'] - result['NEG']
    # NEU contributes 0
    return score

def sentiment_comment(comment, chunk_size=128) -> dict:
    """
    splits comment into chunks and returns average sentiment score,

    returns the average sentiment as a object with POS, NEG, NEU scores.
    """
    if not comment:
        return {'POS': 0.0, 'NEG': 0.0, 'NEU': 0.0}

    chunks = [comment[i:i+chunk_size] for i in range(0, len(comment), chunk_size)]
    score_by_label = {'POS': 0.0, 'NEG': 0.0, 'NEU': 0.0}
    for chunk in chunks:
        result = sentiment_pipeline(chunk, top_k=None)
        for sentiment in result:
            if sentiment['label'] in score_by_label:
                score_by_label[sentiment['label']] += sentiment['score']

    total_chunks = len(chunks)
    assert total_chunks > 0, "total_chunks should be greater than 0"
    
    # average each label's score over all chunks
    for label in score_by_label:
        score_by_label[label] /= total_chunks
    return score_by_label
    

def sentiment_on_topic(brand, topic) -> dict:
    """
    query reddit for submissions mentioning both brand and topic,
    analyze sentiment of submission titles and comments,
    
    returns the average sentiment as a object with POS, NEG, NEU scores.
    """
    # search for submissions mentioning both brand and topic
    submissions = get_submissions(f"{brand} {topic}")
    print(f"Found {len(submissions)} submissions")

    if not submissions:
        return 0.0

    score_by_label = {'POS': 0.0, 'NEG': 0.0, 'NEU': 0.0}
    total_items = 0
    for submission in submissions:
        # for post title
        title_result = sentiment_pipeline(submission.title, top_k=None)
        for sentiment in title_result:
            if sentiment['label'] in score_by_label:
                score_by_label[sentiment['label']] += sentiment['score']
        total_items += 1

        # for comments
        submission.comments.replace_more(limit=0)
        for comment in submission.comments.list():
            if comment.body:
                comment_scores = sentiment_comment(comment.body)
                for label in score_by_label:
                    score_by_label[label] += comment_scores[label]
                total_items += 1

    print(f"Total items analyzed (titles + comments): {total_items}")
    avg_score_by_label = {label: (score / total_items) if total_items else 0.0 for label, score in score_by_label.items()}
    return avg_score_by_label


def attention(brand):
    pass


def sentiment(brand) -> float:
    submissions = [submission for submission in all.search(brand, time_filter="month")]
    print(f"Found {len(submissions)} submissions")

    # top_k=None to returns scores for all labels instead of just the top label
    results = [sentiment_pipeline(submission.title, top_k=None) for submission in submissions]
    
    # # print 5 sample sentiments
    # for i in range(min(5, len(sentiments))):
    #     print(f"Title: {submissions[i].title}")
    #     print(f"Sentiment: {sentiments[i]}")

    # example result: [[{'label': 'NEG', 'score': 0.002347450703382492}, {'label': 'NEU', 'score': 0.0700204074382782}, {'label': 'POS', 'score': 0.9276321530342102}]]
    score_by_label = {'POS': 0.0, 'NEG': 0.0, 'NEU': 0.0}
    for result in results:
        # print(result)
        for sentiment in result:
            score_by_label[sentiment['label']] += sentiment['score']

    print(score_by_label)
    return (score_by_label['POS'] - score_by_label['NEG']) / len(submissions) if submissions else 0.0

# list_of_brands = ["nike", "adidas", "puma", "reebok", "new balance"]

# for brand in list_of_brands:
#     print(f"Sentiment for {brand}: {sentiment(brand)}")


def visualize_sentiment_by_topic_bar_chart(brand, list_of_topics):
    sentiments = [single_score(sentiment_on_topic(brand, topic)) for topic in list_of_topics]

    # bar chart
    plt.bar(list_of_topics, sentiments)
    plt.xlabel("Topics")
    plt.ylabel("Sentiment Score")
    plt.title(f"Sentiment Analysis for {brand} by Topic")
    plt.xticks(rotation=45)
    plt.savefig(f"{brand}_sentiment_by_topic_bar.png")
    plt.close()

def visualize_sentiment_by_topic_pie_chart(brand, list_of_topics):
    sentiments_on_topic = [sentiment_on_topic(brand, topic) for topic in list_of_topics]
    labels = ["NEG", "NEU", "POS"]

    # pie chart for each topic
    fig, axs = plt.subplots(1, len(list_of_topics), figsize=(5 * len(list_of_topics), 5))
    for i, topic in enumerate(list_of_topics):
        sizes = [sentiments_on_topic[i][label] for label in labels]
        axs[i].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        axs[i].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        axs[i].set_title(f"Sentiment for {topic}")
    
    plt.suptitle(f"Sentiment Analysis for {brand} by Topic")
    plt.savefig(f"{brand}_sentiment_by_topic_pie.png")
    plt.close()

brand = "nike"
list_of_topics = ["climate", "sustainability", "diversity", "inclusion", "equity"] 

visualize_sentiment_by_topic_pie_chart(brand, list_of_topics)