import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.write("# Reddit")
st.write("## Sentiment analysis on Reddit ")

# Streamlit app
def create_streamlit_app():

    # side data fileter
    st.sidebar.header("🔧 Data Filter")

    # try to load the data
    try:
        df = pd.read_csv('reddit_brand_data_processed.csv')
        df['date'] = pd.to_datetime(df['date'])
    except:
        st.warning("Unable to load data file; sample data are used.")
        # generate sample data
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', '2024-12-31', freq='D')

        data = []
        brands = ['Nike', 'Adidas', 'New Balance']

        for i in range(1000):
            date = np.random.choice(dates)
            brand = np.random.choice(brands)
            sentiment_score = np.random.normal(
                loc={'Nike': 0.2, 'Adidas': 0.1, 'New Balance': 0.3}[brand],
                scale=0.5
            )

            data.append({
                'id': i,
                'date': date,
                'brand': brand,
                'sentiment_score': max(-1, min(1, sentiment_score)),
                'predicted_sentiment': 'positive' if sentiment_score > 0.1 else 'negative' if sentiment_score < -0.1 else 'neutral',
                'score': np.random.poisson(5),
                'text_length': np.random.randint(50, 500),
                'subreddit': np.random.choice(['sneakers', 'running', 'streetwear', 'fitness'])
            })

        df = pd.DataFrame(data)

    # brand selector
    selected_brands = st.sidebar.multiselect(
        "Select brand",
        options=df['brand'].unique(),
        default=df['brand'].unique()
    )

    # Date selector
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()

    date_range = st.sidebar.date_input(
        "Select time range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # filter
    if len(selected_brands) > 0 and len(date_range) == 2:
        filtered_df = df[
            (df['brand'].isin(selected_brands)) &
            (df['date'].dt.date >= date_range[0]) &
            (df['date'].dt.date <= date_range[1])
            ]
    else:
        filtered_df = df

    # show key indicators
    st.subheader("📊 Key indicators")

    col1, col2 = st.columns(2)

    with col1:
        total_posts = len(filtered_df)
        st.metric("Total posts/comments", f"{total_posts:,}")

    with col2:
        avg_sentiment = filtered_df['sentiment_score'].mean()
        st.metric("Average sentiment score", f"{avg_sentiment:.3f}")

    # Sentiment over time
    st.subheader("📈 Sentiment over time")

    # monthly_trend
    monthly_trend = filtered_df.groupby([filtered_df['date'].dt.to_period('M').astype(str), 'brand'])[
        'sentiment_score'].mean().reset_index()

    fig, ax = plt.subplots(figsize=(10, 6))
    for brand in monthly_trend ['brand'].unique():
        brand_data = monthly_trend[monthly_trend ['brand'] == brand]
        ax.plot(brand_data['date'], brand_data['sentiment_score'], label=brand, marker='o')

    ax.set_title('Monthly brand sentiment score')
    ax.set_xlabel('Month')
    ax.set_ylabel('Sentiment score')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Sentiment distribution
    st.subheader("🍰 Sentiment distribution")

    sentiment_counts = filtered_df.groupby(['brand', 'predicted_sentiment']).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(10, 8))
    sentiment_counts.plot(kind='bar', stacked=True, ax=ax)
    ax.set_title('Brand sentiment distribution')
    ax.set_xlabel('Brand')
    ax.set_ylabel('Post/Comment')
    ax.legend(title='Sentiment category')
    st.pyplot(fig)

    # show raw data
    st.subheader("📋 Raw data")

    if st.checkbox("Show raw data"):
        st.dataframe(filtered_df)

    # download data
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="download cleaned data",
        data=csv,
        file_name="filtered_brand_sentiment_data.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    create_streamlit_app()

