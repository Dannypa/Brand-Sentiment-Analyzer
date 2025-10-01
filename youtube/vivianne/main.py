from youtube.api import *
from youtube.models import *
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
pio.renderers.default = "browser"
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from .fetch_api import fetch_videos, process_video, scale_results
import emoji
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

def main(): 
    def plot_overall_statistics(video_df: pd.DataFrame):
        #Total views + total comments + sentiment distribution per brand

        brand_stats = video_df.groupby("brand").agg(total_views=("views", "sum"),total_likes=("likes", "sum"),total_comments=("comments", "sum")).reset_index()
        
        def sentiment_label(score):
            if score > 0.05:
                return "Positive"
            elif score < -0.05:
                return "Negative"
            else:
                return "Neutral"
        
        video_df["sentiment_label"] = video_df["scaled_result"].apply(sentiment_label)
        sentiment_classes = (video_df.groupby(["brand", "sentiment_label"]).size()).reset_index(name="class_size")
        total_class_size_per_brand = (sentiment_classes.groupby("brand")["class_size"].sum()).reset_index(name="total")
        sentiment_classes = sentiment_classes.merge(total_class_size_per_brand, on="brand")
        sentiment_classes["fraction"] = sentiment_classes["class_size"]/sentiment_classes["total"]
    
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Total Views per Brand", 
                            "Total Likes per Brand", 
                            "Total Comments per Brand", 
                            "Sentiment Fractions per Brand"),
            specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]])

        # Views
        fig.add_trace(go.Bar(x=brand_stats["brand"], y=brand_stats["total_views"], name="Views", marker_color="purple"),row=1, col=1)

        # Likes
        fig.add_trace(go.Bar(x=brand_stats["brand"], y=brand_stats["total_likes"], name="Likes", marker_color="green"),row=1, col=2)

        # Comments
        fig.add_trace(go.Bar(x=brand_stats["brand"], y=brand_stats["total_comments"], name="Comments", marker_color="orange"),row=2, col=1)

        # Sentiment Fractions
        for sentiment, color in zip(["Positive", "Neutral", "Negative"], ["green", "blue", "red"]):
            subset = sentiment_classes[sentiment_classes["sentiment_label"] == sentiment]
            fig.add_trace(go.Bar(x=subset["brand"], y=subset["fraction"],name=sentiment, marker_color=color),row=2, col=2)

        fig.update_layout(
            height=800, width=1000,
            title_text="Brand Overview",
            barmode="stack", 
            legend=dict(title="Metrics & Sentiment", orientation="h", y=-0.15))

        fig.show()

    def plot_daily_video_sentiment(video_df: pd.DataFrame):
        video_df["publishedAt"] = pd.to_datetime(video_df["publishedAt"])
        video_df["date"] = video_df["publishedAt"].dt.date
        daily_video_sentiment = video_df.groupby(["date", "brand"])["scaled_result"].mean().reset_index()
        fig = px.line(daily_video_sentiment,
            x="date",
            y="scaled_result",
            color="brand",
            markers=True,
            title='Daily Average Video Sentiment per Brand',
            labels={"total_sentiment": "Average Sentiment", "date": "Date"}
        )
        fig.update_layout(yaxis=dict(range=[-1, 1]))
        fig.show()

    def plot_daily_comment_sentiment(comment_df: pd.DataFrame):
        if comment_df.empty:
            print("No comments obtained.")
            return
        comment_df["publishedAt"] = pd.to_datetime(comment_df["publishedAt"])
        comment_df["date"] = comment_df["publishedAt"].dt.date
        daily_comment_sentiment = comment_df.groupby(["date", "brand"])["sentiment"].mean().reset_index()
        fig = px.line(daily_comment_sentiment,
            x="date",
            y="sentiment",
            color="brand",
            markers=True,
            title='Daily Average Comment Sentiment per Brand',
            labels={"sentiment": "Average Sentiment", "date": "Date"}
        )
        fig.update_layout(yaxis=dict(range=[-1, 1]))
        fig.show()

    def plot_emoji_cloud(video_df: pd.DataFrame, comment_df: pd.DataFrame):
        def extract_emojis(texts):
            all_emojis = []
            for text in texts:
                for emo in emoji.emoji_list(str(text)):
                    all_emojis.append(emo["emoji"])
            return all_emojis
        
        def emoji_frequency(texts):
            return Counter(extract_emojis(texts))

        texts = []
        if "video_title" in video_df.columns:
            texts.extend(video_df["video_title"].dropna().tolist())
        if "text" in comment_df.columns:
            texts.extend(comment_df["text"].dropna().tolist())
        
        freq = emoji_frequency(texts)
        if not freq:
            print("No emojis found.")
            return

        wc = WordCloud(width=800, height=400, background_color="white", font_path= "C:\Windows\Fonts\seguiemj.ttf").generate_from_frequencies(freq)
        plt.figure(figsize=(12, 6))
        plt.imshow(wc, interpolation="bilinear")
        plt.axis("off")
        plt.title("Emoji cloud from Video Titles and Comments", fontsize=20)
        plt.show()

            
    brands = ["Nike", "Shein", "McDonald's"]
    sent_ana = SentimentIntensityAnalyzer()

    vids_list= []
    total_comments = []
    for brand in brands:
        brand_videos = fetch_videos(brand, days=30)
        for vid in brand_videos:
            video_data, comments = process_video(vid, brand, sent_ana)
            if video_data is None:
                continue
            vids_list.append(video_data)
            total_comments.extend(comments)

    video_df = pd.DataFrame(vids_list)

    if video_df.empty:
        print("No satisfied videos to work with.")
        return

    comment_df = pd.DataFrame(total_comments)

    if comment_df.empty:
        comment_df = pd.DataFrame(columns=["video_id","brand","publishedAt","comment_id","top_level_id","text","sentiment"])

    video_df, min_sent, max_sent = scale_results(video_df)

    #plot_daily_video_sentiment(video_df)
    #plot_daily_comment_sentiment(comment_df)
    plot_overall_statistics(video_df)

    for brand in brands:
        brand_video_df = video_df[video_df["brand"] == brand]
        brand_comment_df = comment_df[comment_df["brand"] == brand]
        plot_emoji_cloud(brand_video_df, brand_comment_df)
        os.makedirs("emoji_clouds", exist_ok=True)
        plt.savefig(f"emoji_clouds/{brand}_emoji_cloud.png", bbox_inches='tight')
        plt.close()


if __name__ == "__main__":
    main()



