CREATE TABLE IF NOT EXISTS youtube_cache (
	id SERIAL PRIMARY KEY,
	video_id VARCHAR(255) UNIQUE NOT NULL,
	query TEXT NOT NULL,
	datetime TIMESTAMP NOT NULL,
	views INTEGER,
	likes INTEGER,
	comments INTEGER,
	avg_comment_sentiment REAL,
	title_sentiment REAL,
	weighted_sentiment REAL GENERATED ALWAYS AS ((title_sentiment * likes * 0.012) + (avg_comment_sentiment * comments * 0.988)) STORED,
	avg_sentiment REAL GENERATED ALWAYS AS ((avg_comment_sentiment + title_sentiment) / 2) STORED
);

CREATE INDEX idx_youtube_cache_query_datetime ON youtube_cache (query, datetime);

CREATE INDEX idx_youtube_cache_video_id ON youtube_cache (video_id);

INSERT INTO youtube_cache (video_id, query, avg_comment_sentiment, datetime) VALUES
('a4', 'This works much better!', 0.9, '2025-11-06 15:00:00+00');

CREATE TABLE IF NOT EXISTS reddit_cache (
	id SERIAL PRIMARY KEY,
	post_id VARCHAR(20) UNIQUE NOT NULL,
	query TEXT NOT NULL,
	subreddit VARCHAR(255) NOT NULL,
	datetime TIMESTAMP NOT NULL,
	title_sentiment REAL,
	avg_comment_sentiment REAL,
	avg_sentiment REAL GENERATED ALWAYS AS ((avg_comment_sentiment + title_sentiment) / 2) STORED
);

CREATE INDEX idx_reddit_cache_subreddit_created ON reddit_cache (query, datetime);

CREATE INDEX idx_reddit_cache_post_id ON reddit_cache (post_id);

INSERT INTO reddit_cache (post_id, query, subreddit, datetime, title_sentiment, avg_comment_sentiment) VALUES
('b1', 'This works much better!', 'testsubreddit', '2025-11-06 15:00:00+00', 0.8, 0.85);
