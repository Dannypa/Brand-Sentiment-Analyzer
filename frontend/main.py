import os
import requests
from dotenv import load_dotenv
import streamlit as st
import plotly.graph_objects as go
import json
import base64

load_dotenv()

HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", 8501))
yt_url = os.environ.get("YT_URL", "http://yt:8080/charts/")
reddit_url = os.environ.get("REDDIT_URL", "http://reddit:8080/charts/")

def decode_binary_data(data_dict):
    if isinstance(data_dict, dict) and 'dtype' in data_dict and 'bdata' in data_dict:
        try:
            binary_data = base64.b64decode(data_dict['bdata'])
            dtype = data_dict['dtype']
            if dtype == 'i1':
                return list(binary_data)
            elif dtype == 'f8': 
                import struct
                return [struct.unpack('d', binary_data[i:i+8])[0] 
                       for i in range(0, len(binary_data), 8)]
            else:
                return list(binary_data)
        except Exception as e:
            st.error(f"Error decoding binary data: {e}")
            return []
    return data_dict

def fix_plotly_data(fig_data):
    if isinstance(fig_data, dict):
        for key, value in fig_data.items():
            if key in ['x', 'y', 'z']:
                fig_data[key] = decode_binary_data(value)
            elif isinstance(value, (dict, list)):
                fix_plotly_data(value)
        if 'type' in fig_data and fig_data['type'] == 'scattermap':
            fig_data['type'] = 'scatter'
        if 'layout' in fig_data and 'template' in fig_data['layout']:
            template = fig_data['layout']['template']
            if 'data' in template and 'scattermap' in template['data']:
                template['data']['scatter'] = template['data'].pop('scattermap', {})
                
    elif isinstance(fig_data, list):
        for item in fig_data:
            if isinstance(item, (dict, list)):
                fix_plotly_data(item)

def create_safe_figure(plotly_data):
    try:
        safe_data = json.loads(json.dumps(plotly_data))
        fix_plotly_data(safe_data)
        if 'data' in safe_data and 'layout' in safe_data:
            fig = go.Figure(data=safe_data['data'], layout=safe_data['layout'])
        elif 'data' in safe_data:
            fig = go.Figure(data=safe_data['data'])
        else:
            fig = go.Figure(safe_data)
            
        return fig
    except Exception as e:
        st.error(f"Error creating figure: {e}")

def render_charts(url: str, brand: str="nike"):
    try:
        st.info("Attempting to fetch data...")
        response = requests.get(f"{url}?brand={brand}", timeout=30)
        
        if response.status_code != 200:
            st.error(f"API returned status code: {response.status_code}")
            st.info(f"Response text: {response.text}")
            return
            
        data = response.json()
        st.success(f"Successfully received data for brand: {brand}")
        
        for obj in data:
            if 'plotly_json' in obj and 'title' in obj:
                try:
                    st.subheader(obj.get("title", "Chart"))
                    fig = create_safe_figure(obj["plotly_json"])
                    st.plotly_chart(fig, use_container_width=True)
                    st.json(obj["plotly_json"])
                    
                except Exception as chart_error:
                    st.error(f"Error rendering chart: {str(chart_error)}")
                    with st.expander("View raw data (debug)"):
                        st.json(obj["plotly_json"])
            
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {str(e)}")
        st.info("Please check if the backend services are running.")
    except json.JSONDecodeError as e:
        st.error(f"Invalid JSON response: {str(e)}")
        st.info(f"Response text: {response.text[:500]}...")
    except Exception as e:
        st.error(f"Something went wrong: {str(e)}")
        st.info("Please check the debug information below.")

st.set_page_config(
    page_title="Brand Sentiment Analysis Dashboard",
    initial_sidebar_state="expanded",
    layout='wide'
)

st.sidebar.title("Settings")

brand = st.sidebar.text_input("Enter a brand:", placeholder="e.g. nike", value="nike")
if 'brands' not in st.session_state:
    st.session_state['brands'] = []
if st.sidebar.button("Add"):
    if not brand:
        st.sidebar.error("It cannot be empty. Please enter a proper brand name.")
    else: 
        st.session_state['brands'].append(brand)
    
st.sidebar.caption("Current brands:")
for brand_item in st.session_state['brands']:
    st.sidebar.write(f"- {brand_item}")
if st.sidebar.button("Clear all"):
    st.session_state.brands.clear()
    st.rerun()

st.title("Sentiment Analysis (CS-C3250 Group 1)")
st.write("Topic: General consumer perceptions of brands.")
st.write("A project for Futurice.")
st.write("This dashboard shows real-time brand sentiment analysis and insights.")

tab_youtube, tab_reddit = st.tabs(["YouTube", "Reddit"])
with tab_youtube:
    st.header("YouTube Sentiment Analysis") 
    render_charts(yt_url, brand)
with tab_reddit:
    st.header("Reddit Sentiment Analysis")
    render_charts(reddit_url, brand)

st.markdown("---")
brands_list = st.session_state.get('brands', [])
brand_str = ", ".join(brands_list)
with st.expander("Debug information"):
    st.write(f"YouTube API URL: {yt_url}")
    st.write(f"Reddit API URL: {reddit_url}")
    st.write(f"Current brand: {brand}")
    st.write(f"All brands: {brand_str}")
    st.write(f"Host: {HOST}, Port: {PORT}")
    
    if st.button("Test Backend Connections"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("Testing YouTube backend...")
            try:
                yt_response = requests.get(f"{yt_url}?brand=nike", timeout=5)
                st.write(f"YouTube backend status: {yt_response.status_code}")
                if yt_response.status_code == 200:
                    st.write("YouTube backend is working!")
            except Exception as e:
                st.write(f"YouTube backend error: {e}")
        
        with col2:
            st.write("Testing Reddit backend...")
            try:
                reddit_response = requests.get(f"{reddit_url}?brand=nike", timeout=5)
                st.write(f"Reddit backend status: {reddit_response.status_code}")
                if reddit_response.status_code == 200:
                    st.write("Reddit backend is working!")
            except Exception as e:
                st.write(f"Reddit backend error: {e}")