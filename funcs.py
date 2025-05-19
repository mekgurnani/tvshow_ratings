import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import time
import requests
from requests.exceptions import SSLError, ConnectionError, Timeout, RequestException

@st.cache_data
def search_tvmaze(query, retries=3, delay=1):
    url = f"https://api.tvmaze.com/search/shows?q={query}"

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)  # increase timeout to be safe
            response.raise_for_status()
            return response.json()
        
        except (SSLError, ConnectionError, Timeout) as e:
            time.sleep(delay)
        
        except RequestException as e:
            st.error(f"Failed to reach TVMaze: {e}")
            break
    
    # If all attempts fail
    st.error("Could not connect to TVMaze after several attempts. Please try again later.")
    return []

@st.cache_data
def load_data(path, retries=3, delay=1):
    for attempt in range(retries):
        try:
            resp = requests.get(path, timeout=5)
            resp.raise_for_status()
            show_data = resp.json()
            episodes_dict = show_data['_embedded']['episodes']

            episodes_data = pd.DataFrame(columns=["name", "season", "episode_number", "episode_rating"])

            for episode in episodes_dict:
                episode_data = pd.DataFrame([{
                    "name": episode['name'], 
                    "season": episode['season'], 
                    "episode_number": episode['number'],
                    "episode_rating": episode['rating']['average']
                }])
                episodes_data = pd.concat([episodes_data, episode_data], ignore_index=True)

            episodes_data = episodes_data.fillna(value=np.nan)
            return show_data, episodes_data

        except (SSLError, ConnectionError) as e:
            time.sleep(delay)
        except Exception as e:
            st.error(f"Unexpected error: {e}")
            break

    st.error("Failed to retrieve data after multiple attempts.")
    return {}, pd.DataFrame()

def find_longest_season(seasons, episodes_data):
    max_episodes = 1
    for season in seasons:
        season_df_shape = (episodes_data[episodes_data['season']==season]).shape[0]
        if season_df_shape > max_episodes:
            max_episodes = season_df_shape

    return max_episodes

def populate_heatmap_input(seasons, episodes_data, ratings_list, episodes_name_list):

    for i, season in enumerate(seasons):
        season_df = episodes_data[episodes_data['season'] == season]
        episode_names = season_df['name'].tolist()
        modified_episode_names = [f"Season {season}, Episode {idx+1}: {name}" for idx, name in enumerate(episode_names)]
        episode_ratings = season_df['episode_rating'].tolist()

        n = len(modified_episode_names)
        episodes_name_list[i][:n] = modified_episode_names

        n = len(episode_ratings)
        ratings_list[i][:n] = episode_ratings

    return episodes_name_list, ratings_list

def plotting_heatmap(episodes_data, show_data, plot_title="📊 Plotting episode ratings for: "):
    seasons = episodes_data['season'].unique()
    rows = len(seasons)
    columns = find_longest_season(seasons, episodes_data)

    rows_plotly = [f"Season {i}" for i in seasons]
    columns_plotly = [f"Episode {i+1}" for i in range(columns)]

    ratings_list = [[np.nan] * columns for _ in range(rows)]
    episodes_name_list = [[np.nan] * columns for _ in range(rows)]

    episodes_name_list, ratings_list = populate_heatmap_input(seasons, episodes_data, ratings_list, episodes_name_list)
    
    episodes_tooltip_list = [
    [
        name if isinstance(name, str) and not pd.isna(name) else "Season has ended"
        for name in row
    ]
    for row in episodes_name_list]
    
    show_name = show_data['name']
    show_language = show_data['language']
    show_status = show_data['status']
    average_rating = show_data['rating']['average']

    streamlit_bg_color = "#0E1117"

    trace1 = go.Heatmap(
        z=[[1 if np.isnan(rating) else np.nan for rating in row] for row in ratings_list],
        x=columns_plotly,
        y=rows_plotly,
        colorscale=[[0, "#222222"], [1, "#222222"]],
        showscale=False,
        hoverinfo="skip",
    )

    trace2 = go.Heatmap(
        z=ratings_list,
        x=columns_plotly,
        y=rows_plotly,
        colorscale="Magma_r",
        colorbar={"title": "Ratings"},
        text=episodes_tooltip_list,
        texttemplate="<b>%{z:.1f}</b>",
        hovertemplate="%{text}<extra></extra>",
        textfont={"size": 18, "color": "dark grey"},
    )

    fig = go.Figure(data=[trace1, trace2])

    # Dynamic sizing 
    min_height = 700
    min_width = 1200
    height_per_row = 20
    width_per_col = 20

    dynamic_height = min_height + (rows - 1) * height_per_row
    dynamic_width = min_width + (columns - 1) * width_per_col

    # Optional cap to prevent excessive size
    dynamic_height = min(dynamic_height, 1800)
    dynamic_width = min(dynamic_width, 2000)

    fig.update_layout(
        hoverlabel=dict(
            font_size=16,
            font_family="Arial",
            bgcolor="rgba(0, 0, 0, 0.8)",
            font_color="white"
        ),
        title={
            "text": (
                f"{show_name} | Language: {show_language} | "
                f"Show status: {show_status} | Overall Rating: {average_rating}"
            ),
            "x": 0.5,
            "y": 0.98,
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 22},
        },
        xaxis={
            "side": "top",
            "tickangle": -45,
            "tickfont": {"size": 18},
        },
        yaxis=dict(
            visible=True,
            autorange="reversed",
            tickfont={"size": 18},
        ),
        height=dynamic_height,
        width=dynamic_width,
        margin=dict(l=180, r=180, t=180, b=180),
    )

    st.subheader(f'{plot_title}{show_name}')
    
    with st.container():
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=False)