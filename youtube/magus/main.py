from api import *
from models import *
from services import *
import matplotlib.pyplot as plt
from statistics import mean
import numpy as np

def main():
    brand_names = ["coca-cola", "pfizer", "apple", "shein"]
    video_count = 500

    sentiment_dict = {}
    attention_dict = {}

    comments_dict = {}
    likes_dict = {}
    views_dict = {}
    
    # New data structures for individual video plotting
    all_video_sentiments = []
    all_video_attentions = []
    all_video_brands = []

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
        
        # Lists to store individual video data for this brand
        video_sentiments_for_brand = []
        video_attentions_for_brand = []

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
                
                # Calculate individual video attention (normalized metrics)
                # We'll normalize these after collecting all data
                video_sentiments_for_brand.append((comment_score + title_score) / 2)
                video_attentions_for_brand.append({
                    'comment_count': comment_count,
                    'view_count': view_count,
                    'like_count': like_count
                })

                # print(f"Like Count: {like_count}, Comment Count: {comment_count}, View Count: {view_count}")
            except Exception as e:
                # print(f"Skipping video {video_id} due to error: {e}")
                continue
            combined_score = (comment_score + title_score) / 2
            comment_sentiments.append(combined_score)

        comments_dict[brand_name] = comment_counts
        likes_dict[brand_name] = like_counts
        views_dict[brand_name] = view_counts

        plt.figure(figsize=(10, 6))
        plt.hist(comment_sentiments, bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('Sentiment Score', fontsize=12)
        plt.ylabel('Frequency', fontsize=12)
        plt.title(f'Histogram of Video Sentiment Scores for {brand_name}', fontsize=14)
        plt.grid(True, alpha=0.3)
        plt.axvline(x=0, color='red', linestyle='--', alpha=0.7, label='Neutral')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{brand_name}_sentiment_histogram.png")
        plt.close()

        sentiment_dict[brand_name] = np.nanmean(comment_sentiments)
        
        # Add individual video data to global lists
        all_video_sentiments.extend(video_sentiments_for_brand)
        all_video_attentions.extend(video_attentions_for_brand)
        all_video_brands.extend([brand_name] * len(video_sentiments_for_brand))

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

    # Create scatter plot for individual videos with different colors for each brand
    if all_video_sentiments and all_video_attentions:
        # Normalize attention scores for individual videos
        all_comment_counts = [video['comment_count'] for video in all_video_attentions]
        all_view_counts = [video['view_count'] for video in all_video_attentions]
        all_like_counts = [video['like_count'] for video in all_video_attentions]
        
        # Calculate normalized attention scores for each video
        normalized_attentions = []
        for video_metrics in all_video_attentions:
            comment_attention = (video_metrics['comment_count'] - min_comments) / (max_comments - min_comments) if max_comments > min_comments else 0
            like_attention = (video_metrics['like_count'] - min_likes) / (max_likes - min_likes) if max_likes > min_likes else 0
            view_attention = (video_metrics['view_count'] - min_views) / (max_views - min_views) if max_views > min_views else 0
            
            # Average the three attention metrics
            avg_attention = (comment_attention + like_attention + view_attention) / 3
            normalized_attentions.append(avg_attention)
        
        # Create the plot with different colors for each brand
        plt.figure(figsize=(12, 8))
        colors = ['red', 'blue', 'green', 'orange']  # Colors for each brand
        brand_color_map = {brand: colors[i] for i, brand in enumerate(brand_names)}
        
        for brand in brand_names:
            # Get indices for this brand
            brand_indices = [i for i, b in enumerate(all_video_brands) if b == brand]
            brand_sentiments = [all_video_sentiments[i] for i in brand_indices]
            brand_attentions = [normalized_attentions[i] for i in brand_indices]
            
            plt.scatter(brand_sentiments, brand_attentions, 
                       c=brand_color_map[brand], label=brand, alpha=0.7, s=50)
        
        plt.xlabel('Sentiment Score', fontsize=14)
        plt.ylabel('Attention Score', fontsize=14)
        plt.title('Individual Video Sentiment vs Attention by Brand', fontsize=16)
        plt.legend(title='Brand', fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # Add reference lines
        plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='Avg Attention')
        plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5, label='Neutral Sentiment')
        
        plt.tight_layout()
        plt.savefig("video_sentiment_attention_by_brand.png", dpi=300, bbox_inches='tight')
        plt.close()

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
    plt.savefig("output.png")

    # print(sentiment_dict)

    # print(attention_dict)

    # print(f"Search query: {search_query}")
    # print(vid_df.head())
        


if __name__ == "__main__":
    main()
