import os
from threading import ExceptHookArgs

import plotly.io as pio
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8501))
yt_url = os.environ.get("YT_URL", "http://yt:8080/charts/multibrand")
reddit_url = os.environ.get("REDDIT_URL", "http://reddit:8080/charts/multibrand")


def render_charts(url: str, brands: list[str], key_start: str = ""):
    if len(brands) == 0:
        st.write("No brands provided.")
        return
    try:
        st.info("Attempting to fetch data...")

        # brand_str = ",".join(brands) #add this line if the backends accept comma-separated in a single parameter
        # st.write(params)
        data = requests.post(url, json=brands).json()
        # st.write(data)

        st.success("Successfully received all the data.")
        # st.info(data)
        for obj in data:
            # st.info(obj)
            try:
                fig = pio.from_json(obj["plotly_json"])
                st.subheader(obj.get("title", "Chart"))
                st.plotly_chart(fig, key=key_start + obj.get("title", "Chart"))
            except Exception as e:
                st.error(f"Failed to produce a chart : {str(e)}")

    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")
        st.info("The data was supposed to be here, but we didn't get it.")


st.set_page_config(
    page_title="Brand Sentiment Analysis Dashboard",
    initial_sidebar_state="expanded",
    layout="wide",
)


st.sidebar.title("Some settings")

brand = st.sidebar.text_input("Enter a brand:", placeholder="e.g. nike")
if (
    "brands" not in st.session_state
):  # needed to preserve information between reruns, https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state
    st.session_state["brands"] = []

if st.sidebar.button("Add", key="add_button"):
    if not brand:
        st.sidebar.error("It cannot be empty. Please enter a proper brand name.")
    elif brand in st.session_state["brands"]:
        st.sidebar.error("This brand is already in the list.")
    else:
        st.session_state["brands"].append(brand)

st.sidebar.caption("Current brands:")
for b in st.session_state["brands"]:
    st.sidebar.write(f"- {b}")

if st.sidebar.button("Clear all", key="clear_button"):
    st.session_state.brands.clear()  # clear the list and rerun after pressing the clear all button
    st.rerun()  # not working


st.title("Sentiment Analysis (CS-C3250 Group 1)")
st.write("Topic: General consumer perceptions of brands.")
st.write("A project for Futurice.")
st.write("This dashboard shows real-time brand sentiment analysis and insights.")

if st.sidebar.button("Generate", key="generate_button"):
    brands_list = st.session_state.get("brands", [])
    # default brands if the list is empty
    # if not brands_list:
    #     default_brands = ["nike", "adidas", "new balance"]
    #     st.session_state["brands"] = default_brands
    #     brands_list = default_brands
    st.write(brands_list)

    tab_youtube, tab_reddit = st.tabs(["YouTube", "Reddit"])
    with tab_youtube:  # youtube subpage
        st.header("YouTube Sentiment Analysis")
        render_charts(yt_url, brands_list, key_start="youtube")
    with tab_reddit:  # reddit subpage
        st.header("Reddit Sentiment Analysis")
        render_charts(reddit_url, brands_list, key_start="reddit")

    st.markdown("---")
    brand_str = ",".join(brands_list)
    with st.expander("Debug information"):
        st.write(f"YouTube API URL: {yt_url}")
        st.write(f"Reddit API URL: {reddit_url}")
        st.write(f"Brand(s): {brand_str}")
        st.write(f"Host: {HOST}, Port: {PORT}")
