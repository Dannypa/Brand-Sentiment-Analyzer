import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta, timezone
from collections import Counter
import emoji

# PLOTLY VISUALIZATIONS

def plot_histogram(df: pd.DataFrame, group_by='subreddit', timeframe='month'):
    """Histogram of sentiment distribution"""
    today = datetime.now(timezone.utc).date()
    df_filtered = df.copy()
    
    if timeframe == 'week':
        df_filtered = df_filtered[df_filtered['date'] >= today - timedelta(days=7)]
    elif timeframe == 'yesterday':
        df_filtered = df_filtered[df_filtered['date'] == today - timedelta(days=1)]
    
    fig = px.histogram(
        df_filtered, 
        x='sentiment', 
        color=group_by,
        nbins=20, 
        barmode='overlay', 
        opacity=0.6,
        title=f'Sentiment Distribution ({timeframe.title()})'
    )
    fig.update_layout(
        xaxis_title='Sentiment Polarity (-1 = neg, +1 = pos)',
        yaxis_title='Frequency',
        template='plotly_white'
    )
    return fig

def plot_timeseries(df: pd.DataFrame, group_by='subreddit'):
    """Daily average sentiment timeseries"""
    daily = df.groupby([group_by, 'date'])['sentiment'].mean().reset_index()
    
    fig = px.line(
        daily, 
        x='date', 
        y='sentiment', 
        color=group_by,
        markers=True,
        title='Daily Average Sentiment'
    )
    fig.update_layout(
        yaxis_title='Average Sentiment (-1 to +1)',
        template='plotly_white'
    )
    return fig
    
def plot_emoji_donut(df: pd.DataFrame, top_n=15):
    """Donut chart of top emojis"""
    df['emojis'] = df['content'].apply(lambda text: 
        [c for c in str(text) if c in emoji.EMOJI_DATA] if pd.notna(text) else []
    )
    
    all_emojis = [e for sublist in df['emojis'] for e in sublist]
    
    if not all_emojis:
        return None
    
    emoji_counts = Counter(all_emojis).most_common(top_n)
    emoji_df = pd.DataFrame(emoji_counts, columns=['Emoji', 'Count'])
    
    fig = px.pie(
        emoji_df, 
        values='Count', 
        names='Emoji',
        hole=0.5,
        title=f'Top {top_n} Emojis Distribution'
    )
    fig.update_traces(
        textposition='outside',
        texttemplate='%{label}<br>%{percent:.1%}',
        textfont_size=10
    )
    return fig

# === MATPLOTLIB VISUALIZATIONS ===

def plot_monthly_sentiment(df: pd.DataFrame, group_by='keyword', brand_colors=None):
    """Monthly sentiment line plot"""
    df = df.copy()
    df['month'] = pd.to_datetime(df['created_utc'], unit='s').dt.to_period('M')
    
    monthly = df.groupby(['month', group_by]).agg({
        'sentiment': 'mean',
        'id': 'count'
    }).rename(columns={'id': 'post_count', 'sentiment': 'avg_sentiment'}).reset_index()
    
    fig, ax = plt.subplots(figsize=(16, 10))
    
    for group in monthly[group_by].unique():
        group_data = monthly[monthly[group_by] == group]
        color = brand_colors.get(group) if brand_colors else None
        ax.plot(
            range(len(group_data)), 
            group_data['avg_sentiment'],
            marker='o', 
            linewidth=1.5,
            label=group,
            color=color,
            markersize=5
        )
    
    plt.title('Sentiment Over Time (Monthly)')
    plt.xlabel('Month')
    plt.ylabel('Average Sentiment Score')
    plt.legend()
    plt.tight_layout()
    return fig

def plot_weekly_sentiment(df: pd.DataFrame, group_by='keyword', brand_colors=None):
    """Weekly sentiment line plot with seaborn"""
    df = df.copy()
    df['created_date'] = pd.to_datetime(df['created_utc'], unit='s')
    df['year'] = df['created_date'].dt.year
    df['week'] = df['created_date'].dt.isocalendar().week
    df['year_week'] = df['year'].astype(str) + '-W' + df['week'].astype(str).str.zfill(2)
    
    weekly = df.groupby(['year_week', group_by]).agg({
        'sentiment': 'mean',
        'id': 'count'
    }).rename(columns={'id': 'post_count', 'sentiment': 'avg_sentiment'}).reset_index()
    
    sns.set_style('white')
    plt.figure(figsize=(16, 8))
    
    sns.lineplot(
        data=weekly,
        x='year_week',
        y='avg_sentiment',
        hue=group_by,
        palette=brand_colors,
        marker='o',
        markersize=5,
        linewidth=1.5
    )
    
    plt.title('Sentiment Over Time (Weekly)')
    plt.xlabel('Week')
    plt.ylabel('Average Sentiment Score')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(-0.5, 0.5)
    plt.yticks(np.arange(-0.5, 0.6, 0.1))
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    return plt.gcf()

def plot_sentiment_by_topic_bar(brand: str, topics: list, sentiments: list):
    """Bar chart for sentiment by topic"""
    plt.figure(figsize=(10, 6))
    plt.bar(topics, sentiments)
    plt.xlabel('Topics')
    plt.ylabel('Sentiment Score')
    plt.title(f'Sentiment Analysis for {brand} by Topic')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt.gcf()

def plot_sentiment_by_topic_pie(brand: str, topics: list, sentiments_dict: list):
    """Pie charts for sentiment by topic (NEG/NEU/POS breakdown)"""
    labels = ['NEG', 'NEU', 'POS']
    
    fig, axs = plt.subplots(1, len(topics), figsize=(5 * len(topics), 5))
    if len(topics) == 1:
        axs = [axs]
    
    for i, topic in enumerate(topics):
        sizes = [sentiments_dict[i][label] for label in labels]
        axs[i].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        axs[i].axis('equal')
        axs[i].set_title(f'Sentiment for {topic}')
    
    plt.suptitle(f'Sentiment Analysis for {brand} by Topic')
    plt.tight_layout()
    return fig