# Data Science Project 2025 Group 1

## Description

We provide a Streamlit web application that shows interactive Plotly visualizations of the sentiment of users towards brands based on data collected from YouTube and Reddit.

## Installation

First, you need to clone the project from our repository down to your local machine. You can clone it through 

```
git clone git@version.aalto.fi:parniud1/data-science-project-2025-group-1.git
```
or 

```
git clone https://version.aalto.fi/gitlab/parniud1/data-science-project-2025-group-1.git
```
You will also need to create .env files in the reddit-backend and yt-backend folder with the following structure (the keys are obtained through Reddit and Youtube APIs):
In the reddit-backend folder: 
```
REDDIT_APP_SECRET= 
REDDIT_APP_NAME= 
REDDIT_APP_ID=t

ML_URL = http://ml:8080/get_sentiment

```
In the yt-backend folder:
```
YOUTUBE_KEY =  

ML_URL = http://ml:8080/get_sentiment

DB_HOST=db
DB_NAME=data
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres

```

## Running

To run the project, you need docker installed. Follow the instructions for your os: https://docs.docker.com/engine/install/.

After that, running the project should be as simple as executing

```
docker compose up --build
```

in the root of the repository.

After running the project, you can go to http://localhost:3001/ to start using our website. Click on the white bar, type in the brand(s) you want to explore and press "Add", then press "Generate" to generate the visualizations.

***


