import pandas as pd
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from transformers import pipeline

# Initialize sentiment analyzers
vader_analyzer = SentimentIntensityAnalyzer()
bertweet_pipeline = None  # Lazy load

def clean_text(text):
    """Clean text for sentiment analysis"""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_sentiment_vader(text: str) -> float:
    """VADER sentiment: returns compound score (-1 to 1)"""
    if not text:
        return 0.0
    return vader_analyzer.polarity_scores(text)["compound"]

def get_sentiment_textblob(text: str) -> float:
    """TextBlob sentiment: returns polarity (-1 to 1)"""
    if not text:
        return 0.0
    return TextBlob(text).sentiment.polarity

def get_sentiment_bertweet(text: str, chunk_size=128) -> dict:
    """BERTweet sentiment: returns {POS, NEG, NEU} scores"""
    global bertweet_pipeline
    if bertweet_pipeline is None:
        bertweet_pipeline = pipeline(model="finiteautomata/bertweet-base-sentiment-analysis")
    
    if not text:
        return {'POS': 0.0, 'NEG': 0.0, 'NEU': 0.0}
    
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    score_by_label = {'POS': 0.0, 'NEG': 0.0, 'NEU': 0.0}
    
    for chunk in chunks:
        result = bertweet_pipeline(chunk, top_k=None)
        for sentiment in result:
            if sentiment['label'] in score_by_label:
                score_by_label[sentiment['label']] += sentiment['score']
    
    total_chunks = len(chunks)
    for label in score_by_label:
        score_by_label[label] /= total_chunks
    
    return score_by_label

def bertweet_to_single_score(result: dict) -> float:
    """Convert BERTweet result to single score (-1 to 1)"""
    return result['POS'] - result['NEG']

def categorize_sentiment(score: float) -> str:
    """Categorize sentiment score into labels"""
    if score > 0.8:
        return 'Very Positive'
    elif score > 0.1:
        return 'Positive'
    elif score < -0.8:
        return 'Very Negative'
    elif score < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

def analyze_dataframe(df: pd.DataFrame, method='vader'):
    """Add sentiment columns to dataframe"""
    df = df.copy()
    df['cleaned_content'] = df['content'].apply(clean_text)
    
    if method == 'vader':
        df['sentiment'] = df['cleaned_content'].apply(get_sentiment_vader)
    elif method == 'textblob':
        df['sentiment'] = df['cleaned_content'].apply(get_sentiment_textblob)
    elif method == 'bertweet':
        df['sentiment_dict'] = df['cleaned_content'].apply(get_sentiment_bertweet)
        df['sentiment'] = df['sentiment_dict'].apply(bertweet_to_single_score)
    
    df['sentiment_category'] = df['sentiment'].apply(categorize_sentiment)
    df['date'] = pd.to_datetime(df['created_utc'], unit='s').dt.date
    
    return df