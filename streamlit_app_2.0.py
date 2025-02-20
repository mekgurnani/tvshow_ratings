import requests
import logging
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from funcs import load_data, find_longest_season, populate_heatmap_input, plotting_heatmap

st.set_page_config(layout="wide")

BASE_URL = 'https://api.tvmaze.com'

logging.basicConfig(level=logging.DEBUG)

st.title(f'TV Show Ratings Heatmap')

# 0. User selects show to viz
@st.cache_data
def get_available_shows():
    response = requests.get(f"{BASE_URL}/shows")
    if response.status_code == 200:
        data = response.json()
        # Create a dictionary mapping show name to show id
        show_info = {show["name"]: show["id"] for show in data}
        return show_info
    return {}

available_shows = get_available_shows()
show_names = sorted(available_shows.keys())

selected_show = st.selectbox("Choose a show:", show_names)

selected_show_id = available_shows.get(selected_show)

# 1. Load all data and episode specific data

path = f'{BASE_URL}/shows/{selected_show_id}?embed=episodes'

show_data, episodes_data = load_data(path)

episodes_data = episodes_data.fillna(value=np.nan)

# 2. get other metadata
# data_load_state.text("Loading data...done!")

data_load_state = st.text('Collecting ratings data to be plotted...')

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
