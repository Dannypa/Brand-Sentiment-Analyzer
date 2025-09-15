from api import *
from models import *
from services import *

def main():
    brand_name = "nike"
    search_queries = [f"{brand_name} sustainability", f"{brand_name} ecofriendly", f"{brand_name} greenwashing"]
    video_count = 10

    print("Brand:", brand_name)
    print("Search queries:", search_queries)

    for search_query in search_queries:
        videos = search_videos(search_query, max_results=video_count)
        videos = searchListResponse(**videos)
        vid_df = video_to_dataframe(videos)

        # for video_id in vid_df['video_id']:
        #     comments = get_comments(video_id, max_results=20)
        #     comments = commentListResponse(**comments)
            
        # comments_dict = get_comment_reply_dict
        # comment_df = comments_to_dataframe

        print(f"Search query: {search_query}")
        print(vid_df.head())
        


if __name__ == "__main__":
    main()
