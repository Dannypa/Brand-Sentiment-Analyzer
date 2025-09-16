from api import *
from models import *
from services import *
import matplotlib.pyplot as plt

def main():
    brand_name = "oatly"
    video_count = 100

    print("Brand:", brand_name)

    videos = search_videos(brand_name, max_results=video_count, start_date="2023-01-01T00:00:00Z", end_date="2024-01-01T00:00:00Z")
    videos = searchListResponse(**videos)
    vid_df = video_to_dataframe(videos)

    print(vid_df.head())

    all_sentiment_scores = []

    for video_id in vid_df['video_id']:
        comment_count = vid_df.loc[vid_df['video_id'] == video_id, 'comment_count'].values[0]
        if comment_count == 0 or pd.isna(comment_count):
            continue

        try:
            comments = get_comments(video_id, max_results=50)
            comments = commentListResponse(**comments)
            top_level_comments = comments_to_list_of_top_level(comments)
            sentiment_scores = map(lambda x: sentiment_score(x)["compound"], top_level_comments)
            # for score in sentiment_scores:
            #     print(score)
        except Exception as e:
            print(f"Skipping video {video_id} due to error: {e}")
            continue
        all_sentiment_scores.extend(sentiment_scores)
        print(all_sentiment_scores)

    
    plt.hist(all_sentiment_scores, bins=20, edgecolor='black')
    plt.xlabel('Sentiment Score')
    plt.ylabel('Number of Comments')
    plt.title('Histogram of Comment Sentiment Scores')
    plt.show()

        

    # print(f"Search query: {search_query}")
    # print(vid_df.head())
        


if __name__ == "__main__":
    main()
