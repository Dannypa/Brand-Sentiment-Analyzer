from api import *
from models import *
from services import *
import matplotlib.pyplot as plt
from statistics import mean
import numpy as np

def main():
    brand_names = ["coca-cola", "pfizer", "apple", "shein"]
    video_count = 100

    sentiment_dict = {}
    attention_dict = {}

    comments_dict = {}
    likes_dict = {}
    views_dict = {}

    max_comments = 0
    max_likes = 0
    max_views = 0

    min_comments = float('inf')
    min_likes = float('inf')
    min_views = float('inf')

    for brand_name in brand_names:
        # print(f"Processing brand: {brand_name}")
        videos = search_videos(f"{brand_name} bad", max_results=video_count, start_date="2023-01-01T00:00:00Z", end_date="2024-01-01T00:00:00Z")
        videos = searchListResponse(**videos)
        vid_df = video_to_dataframe(videos)
        vid_df['comment_count'] = pd.to_numeric(vid_df['comment_count'], errors='coerce')
        vid_df['view_count'] = pd.to_numeric(vid_df['view_count'], errors='coerce')
        vid_df['like_count'] = pd.to_numeric(vid_df['like_count'], errors='coerce')
        vid_df = remove_videos_without_comments(vid_df)
        vid_df = remove_videos_without_brand_title(vid_df, brand_name)
    
        comment_sentiments = []
        comment_counts = []
        view_counts = []
        like_counts = []

        for video_id in vid_df['video_id']:
            comment_count = vid_df.loc[vid_df['video_id'] == video_id, 'comment_count'].values[0]
            if comment_count == 0 or pd.isna(comment_count):
                continue

            try:
                comments = get_comments(video_id, max_results=50)
                comments = commentListResponse(**comments)
                top_level_comments = comments_to_list_of_top_level(comments)
                comment_scores = map(lambda x: sentiment_score(x)["compound"], top_level_comments)
                comment_score = np.nanmean(list(comment_scores))
                title = vid_df.loc[vid_df['video_id'] == video_id, 'title'].values[0]
                title_score = sentiment_score(title)["compound"]

                view_count = vid_df.loc[vid_df['video_id'] == video_id, 'view_count'].values[0]
                like_count = vid_df.loc[vid_df['video_id'] == video_id, 'like_count'].values[0]

                comment_counts.append(comment_count)
                view_counts.append(view_count)
                like_counts.append(like_count)

                # print(f"Like Count: {like_count}, Comment Count: {comment_count}, View Count: {view_count}")
            except Exception as e:
                # print(f"Skipping video {video_id} due to error: {e}")
                continue
            combined_score = (comment_score + title_score) / 2
            comment_sentiments.append(combined_score)

        comments_dict[brand_name] = comment_counts
        likes_dict[brand_name] = like_counts
        views_dict[brand_name] = view_counts

        sentiment_dict[brand_name] = np.nanmean(comment_sentiments)

        if comment_count > max_comments:
            max_comments = comment_count
        if view_count > max_views:
            max_views = view_count
        if like_count > max_likes:
            max_likes = like_count

        if comment_count < min_comments:
            min_comments = comment_count
        if view_count < min_views:
            min_views = view_count
        if like_count < min_likes:
            min_likes = like_count

        # print(f"Average sentiment score for {brand_name}: {mean(all_sentiment_scores) if all_sentiment_scores else 'N/A'}")
        
    
    # for brand in brand_names:

    for brand_name in brand_names:
        comments_counts = comments_dict[brand_name]
        likes_counts = likes_dict[brand_name]
        views_counts = views_dict[brand_name]

        comment_attentions = [(c - min_comments) / (max_comments - min_comments) for c in comments_counts]
        like_attentions = [(l - min_likes) / (max_likes - min_likes) for l in likes_counts]
        view_attentions = [(v - min_views) / (max_views - min_views) for v in views_counts]

        avg_comment_attention = np.nanmean(comment_attentions)
        avg_like_attention = np.nanmean(like_attentions)
        avg_view_attention = np.nanmean(view_attentions)

        attention_score = (avg_comment_attention + avg_like_attention + avg_view_attention) / 3

        attention_dict[brand_name] = attention_score

    sentiment_values = [sentiment_dict[brand] for brand in brand_names]
    attention_values = [attention_dict[brand] for brand in brand_names]

    plt.scatter(sentiment_values, attention_values, s=100, alpha=0.7)
    
    for i, brand in enumerate(brand_names):
        plt.annotate(f"{brand}", (sentiment_values[i], attention_values[i]), 
                    xytext=(5, 5), textcoords='offset points', fontsize=12)
    
    plt.xlabel('Sentiment Score', fontsize=14)
    plt.ylabel('Attention Score', fontsize=14)
    plt.title('Brand Sentiment vs Attention Analysis', fontsize=16)
    plt.grid(True, alpha=0.3)
    
    plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
    

    plt.xlim(min(sentiment_values) - 0.1, max(sentiment_values) + 0.1)
    plt.ylim(min(attention_values) - 0.1, max(attention_values) + 0.1)
    
    plt.tight_layout()
    plt.show()

    # print(sentiment_dict)

    # print(attention_dict)

    # print(f"Search query: {search_query}")
    # print(vid_df.head())
        


if __name__ == "__main__":
    main()
