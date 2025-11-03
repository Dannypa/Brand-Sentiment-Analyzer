from wordcloud import WordCloud
import numpy as np
from charts.latest_histogram import get_scaled_dfs

def word_cloud(brands: list[str]) -> np.array:
    _, comment_df = get_scaled_dfs(brands, days=30)
    text = " ".join(comment_df["text"].tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    return wordcloud.to_array()
