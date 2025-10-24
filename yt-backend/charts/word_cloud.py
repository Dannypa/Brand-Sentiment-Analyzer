from wordcloud import WordCloud
import numpy as np

def word_cloud() -> np.array:
    text = "Sample text for word cloud generation. This text can be replaced with actual data."
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    return wordcloud.to_array()
