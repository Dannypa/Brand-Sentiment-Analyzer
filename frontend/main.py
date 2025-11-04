import os
import requests
from dotenv import load_dotenv
import streamlit as st
import plotly.io as pio
import plotly.express as px

load_dotenv()

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8501))
yt_url = os.environ.get("YT_URL", "http://yt:8080/charts/")
reddit_url = os.environ.get("REDDIT_URL", "http://reddit:8080/charts/")


def render_charts(url: str, brand: str="nike", key_start: str=""):
    try:
        st.info("Attempting to fetch data...")
        data = requests.get(f"{url}?brand={brand}").json()
        st.info(data)
        for obj in data:
            # st.info(obj)
            fig = pio.from_json(obj["plotly_json"])
            st.subheader(obj.get("title", "Chart"))
            st.plotly_chart(fig, key=key_start+obj.get("title", "Chart"))
            
    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")
        st.info(f"The data was supposed to be here, but we didn't get it.")
        

st.set_page_config(
    page_title="Brand Sentiment Analysis Dashboard",
    initial_sidebar_state="expanded",
    layout='wide'
)


st.sidebar.title("Some settings")

brand = st.sidebar.text_input("Enter a brand:", placeholder="e.g. nike")
if 'brands' not in st.session_state: #needed to preserve information between reruns, https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
    st.session_state['brands'] = []

if st.sidebar.button("Add", key="add_button"):
    if not brand:
        st.sidebar.error("It cannot be empty. Please enter a proper brand name.")
    else: 
        st.session_state['brands'].append(brand)
    
st.sidebar.caption("Current brands:")
for brand in st.session_state['brands']:
    st.sidebar.write(f"- {brand}")

if st.sidebar.button("Clear all", key="clear_button"):
    st.session_state.brands.clear() #clear the list and rerun after pressing the clear all button
    st.rerun() #not working


st.title("Sentiment Analysis (CS-C3250 Group 1)")
st.write("Topic: General consumer perceptions of brands.")
st.write("A project for Futurice.")
st.write("This dashboard shows real-time brand sentiment analysis and insights.")

tab_youtube, tab_reddit = st.tabs(["YouTube", "Reddit"])
with tab_youtube: #youtube subpage
    st.header("YouTube Sentiment Analysis") 
    render_charts(yt_url, brand, key_start="youtube")
with tab_reddit: #reddit subpage
    st.header("Reddit Sentiment Analysis")
    render_charts(reddit_url, brand, key_start="reddit")


st.markdown("---")
brands_list = st.session_state.get('brands', [])
brand_str = ", ".join(brands_list)
with st.expander("Debug information"):
    st.write(f"YouTube API URL: {yt_url}")
    st.write(f"Reddit API URL: {reddit_url}")
    st.write(f"Brand(s): {brand_str}")
    st.write(f"Host: {HOST}, Port: {PORT}")