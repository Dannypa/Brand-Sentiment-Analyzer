from api import *
from models import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def main(): 
    brand = "Nike"
    q = f'{brand.lower()} AND ("good" OR "bad")'
    page_token = None
    pages = 10
    all_videos = []

    sent_ana = SentimentIntensityAnalyzer()

    for i in range(pages):
        videos = search_videos(query = q, max_results = 100, start_date = "2024-01-01T00:00:00Z",end_date = "2025-09-17T00:00:00Z", page_token = page_token)
        videos = searchListResponse(**videos)

        all_videos.extend(videos.items)
        page_token = videos.nextPageToken
        if not page_token:
            break

    vids_list = []
    for vid in all_videos:
        video_id = vid.id.videoId
        video_title = vid.snippet.title
        video_details = get_video_details(video_id)
        video_details = videoListResponse(**video_details)

        video_views = int(video_details.items[0].statistics.viewCount or 0)
        video_likes = int(video_details.items[0].statistics.likeCount or 0)
        video_comments = int(video_details.items[0].statistics.commentCount or 0)

#--------exclude <5000 views & brand name not in video title
        if video_views >= 5000 and brand.lower() in video_title.lower(): 
            vid_comments = get_comments(video_id)
            vid_comments = commentListResponse(**vid_comments)
            all_comments = []
#----------comments + replies
            for c in vid_comments.items: 
                comment = c.snippet.topLevelComment.snippet
                all_comments.append({
                    "video_id": c.snippet.videoId,  
                    "comment_id": c.snippet.topLevelComment.id,
                    "top_level_id": None,      
                    "text": comment.textOriginal
                })

                if c.replies: 
                    for reply in c.replies.get("comments", []): 
                        all_comments.append({
                            "video_id": c.snippet.videoId,  
                            "comment_id": reply.id,
                            "top_level_id": reply.snippet.parentId,      
                            "text": reply.snippet.textOriginal
                        })
#sentiment
            sentiment_scores = []
            for comment in all_comments:
                score = sent_ana.polarity_scores(comment["text"])["compound"]
                sentiment_scores.append(score)
            if sentiment_scores:
                s_comments = sum(sentiment_scores)/len(sentiment_scores) 
            else: 
                s_comments = 0
            s_video = sent_ana.polarity_scores(str(video_title))["compound"]

            w_likes = 0.012
            w_comments = 0.988
            total_s = s_video * video_likes* w_likes + s_comments*video_comments*w_comments

            vids_list.append({
                    "video_id": video_id,
                    "video_title": video_title,
                    "views": video_views,
                    "likes": video_likes,
                    "comments": video_comments, 
                    "sentiment_comments": s_comments,
                    "sentiment_video": s_video,
                    "total_sentiment": total_s
                })
            
    video_df = pd.DataFrame(vids_list)
    
    if video_df.empty:
        print("No satisfied videos to work with.")
    else: 

        min_sent = video_df["total_sentiment"].min()
        max_sent = video_df["total_sentiment"].max()

        if min_sent == max_sent: 
            video_df["scaled_result"] = 0
        else: 
            video_df["scaled_result"] = (2*video_df["total_sentiment"] - max_sent - min_sent)/(max_sent-min_sent)

        print(video_df.shape)


        plt.figure(figsize=(10,6))
        plt.hist(video_df["scaled_result"], bins=20, edgecolor = 'black')
        plt.xlabel("Sentiment score [-1;1]")
        plt.ylabel("Number of videos")
        plt.title(f"Up-to-date sentiment distribution of {brand} (last year until now)")
        plt.show()


if __name__ == "__main__":
    main()



