import requests
import logging
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from funcs import search_tvmaze, load_data, find_longest_season, populate_heatmap_input, plotting_heatmap

st.set_page_config(layout="wide")

BASE_URL = 'https://api.tvmaze.com'

logging.basicConfig(level=logging.DEBUG)

st.title(f'TV Show Ratings Heatmap')

query = st.text_input("Enter a show name:")

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

option = st.selectbox(
    "Choose the show you were looking for",
    retrieved_data
)

if option:
    selected_show_id = show_dict.get(option)  

    if selected_show_id:
    
        path = f'{BASE_URL}/shows/{selected_show_id}?embed=episodes'

        show_data, episodes_data = load_data(path)

        episodes_data = episodes_data.fillna(value=np.nan)

        if episodes_data['episode_rating'].isnull().all():
            st.warning(f"No ratings data for {show_data['name']} recorded on TV Maze, choose another show!")

        else:   
            # defining heatmap dimensions
            seasons = episodes_data['season'].unique()
            rows = len(seasons) # number of seasons
            columns = find_longest_season(seasons, episodes_data)

            # populating input data for plotly heatmaps
            rows_plotly = [f"Season {i}" for i in seasons]
            columns_plotly = [f"Episode {i+1}" for i in range(columns)]

            ratings_list = [[np.nan] * columns for _ in range(rows)]
            episodes_name_list = [[np.nan] * columns for _ in range(rows)]

            episodes_name_list, ratings_list = populate_heatmap_input(seasons, episodes_data, ratings_list, episodes_name_list)

            st.subheader(f'📊 Plotting episode ratings for {show_data['name']}')

            # streamlit version
            plotting_heatmap(ratings_list, episodes_name_list, rows_plotly, columns_plotly, show_data)

    else:
        st.write("Please select a show.")

