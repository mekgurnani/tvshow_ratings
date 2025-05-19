import requests
import logging
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from funcs import search_tvmaze, load_data, find_longest_season, populate_heatmap_input, plotting_heatmap

st.set_page_config(layout="wide")
st.markdown("""
    <style>
    /* Fix: Style selectbox label, which is a <p> tag inside the selectbox */
    div[data-testid="stSelectbox"] p {
        font-size: 20px !important;
        font-weight: bold !important;
        margin-bottom: 0.25rem !important;
    }
    </style>
""", unsafe_allow_html=True)

url = "https://github.com/mekgurnani"
st.markdown(
    f"""
    <div style='text-align: right; font-size: 16px;'>
        <a href="{url}" target="_blank">Check out my GitHub profile</a>
    </div>
    """,
    unsafe_allow_html=True
)

BASE_URL = 'https://api.tvmaze.com'

logging.basicConfig(level=logging.DEBUG)

st.title("📺 TV Show Ratings Explorer")

st.markdown(
    """
    <div style='font-size: 20px; line-height: 1.6'>
        <em>Tired of getting spoilers from friends but still want to know if the episode was worth it?</em><br>
        Search for any TV show and explore how each season unfolds with this interactive heatmap, powered by data from 
        <a href='https://www.tvmaze.com' target='_blank'>TVMaze</a>.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    div[data-testid="stTextInput"] p {
        font-size: 20px !important;
        font-weight: bold !important;
    }
    </style>
""", unsafe_allow_html=True)
query = st.text_input("Enter a show name:")

# show plotted by default - black mirror
current_show_path = "https://api.tvmaze.com/shows/305?embed=episodes"
default_show_data, default_episodes_data = load_data(current_show_path)

if not query:
    plotting_heatmap(default_episodes_data, default_show_data, plot_title="What I am watching currently: ")

else:
    retrieved_data = []
    show_dict = {}

    if query:
        results = search_tvmaze(query)
        if results:
            for show in results:
                show_data = show["show"]
                show_network = show_data.get("network", None)
                name = f"{show_data["name"]} "
                show_id = f"{show_data["id"]}"
                genre = f"Genre: {', '.join(show_data.get('genres', ['N/A'])) if show_data.get('genres') else 'Unknown'}"               # join(show_data.get('genres', []))}"
                language = (f"; Language: {show_data.get('language', 'N/A')}" )
                premiered = (f"; Premiered on: {show_data.get('premiered', 'N/A')}")

                if show_network:
                    country = f"; Country of origin: {show_network.get('country', {}).get('name', 'N/A')}"
                else:
                    country = "; Country of origin: N/A"  # Handle case when network is None

                option = f"{name}({genre}{language}{premiered}{country})"
                retrieved_data.append(option) 
                show_dict[option] = show_id
                        
        else:
            st.error("No results found.")


    option = st.selectbox("Choose the show you were looking for", retrieved_data)

    if option:
        selected_show_id = show_dict.get(option)  

        if selected_show_id:
        
            path = f'{BASE_URL}/shows/{selected_show_id}?embed=episodes'

            show_data, episodes_data = load_data(path)

            if episodes_data['episode_rating'].isnull().all():
                st.warning(f"No ratings data for {show_data['name']} recorded on TV Maze, choose another show!")

            else:   
                # streamlit version
                plotting_heatmap(episodes_data, show_data)

        else:
            st.write("Please select a show.")


