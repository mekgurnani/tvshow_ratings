import requests
import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

@st.cache_data
def search_tvmaze(query):
    url = f"https://api.tvmaze.com/search/shows?q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

@st.cache_data
def load_data(path):
    
    resp = requests.get(path, timeout=1)
    show_data = resp.json()
    episodes_dict = show_data['_embedded']['episodes']

    episodes_data = pd.DataFrame(columns=["name", "season", "episode_number", "episode_rating"])

    for episode in episodes_dict:
        episode_data = pd.DataFrame([{"name": episode['name'], 
                                        "season": episode['season'], 
                                        "episode_number": episode['number'],
                                        "episode_rating": episode['rating']['average']}])
        episodes_data = pd.concat([episodes_data, episode_data], ignore_index=True)

    return show_data, episodes_data

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

def plotting_heatmap(ratings_list, episodes_name_list, rows_plotly, columns_plotly, show_data):

    show_name = show_data['name']
    show_language = show_data['language']
    show_status = show_data['status']
    average_rating = show_data['rating']['average']

    streamlit_bg_color = "#0E1117"

    trace1 = go.Heatmap(
        z=[[1 if np.isnan(rating) else np.nan for rating in row] for row in ratings_list],
        x=columns_plotly,
        y=rows_plotly,
        colorscale=[[0, streamlit_bg_color], [1, streamlit_bg_color]],  # Match background
        showscale=False,
        hoverinfo="skip",
    )

    trace2 = go.Heatmap(
        z=ratings_list,
        x=columns_plotly,
        y=rows_plotly,
        colorscale="Magma_r",
        colorbar={"title": "Ratings"},  # Reduce colorbar size
        text=episodes_name_list,
        texttemplate="<b>%{z:.1f}</b>",  # Show numbers inside cells with one decimal place
        hovertemplate="%{text}<extra></extra>",
        textfont={"size": 18, "color": "dark grey"},
    )

    # Create the figure
    fig = go.Figure(data=[trace1, trace2])

    fig.update_layout(
        hoverlabel=dict(
            font_size=16,  # Increase font size
            font_family="Arial",  # Change font if needed
            bgcolor="rgba(0, 0, 0, 0.8)",  # Optional: Change background color for better contrast
            font_color="white"  # Optional: Change font color for readability
        ),
        title={
            "text": (
                f"{show_name} | Language: {show_language} | "
                f"Show status: {show_status} | Overall Rating: {average_rating}"
            ),
            "x": 0.5,  # Center align title
            "y": 0.98,  # Push title slightly higher
            "xanchor": "center",
            "yanchor": "top",
            "font": {"size": 22},  # Increase title font size
        },
        xaxis={
            "side": "top",
            "tickangle": -45,  # Rotate x-axis labels
            "tickfont": {"size": 18},  # Increase font size of labels
        },
        yaxis=dict(
            visible=True,
            autorange="reversed",
            tickfont={"size": 18},  # Increase font size of y-axis labels
        ),
        height=700,  # Increased height
        width=1200,  # Increased width
        margin=dict(l=180, r=180, t=180, b=180),  # More space for x-axis labels
    )

    fig.update_layout(
        hoverlabel=dict(
            font_size=16,  # Increase font size
            font_family="Arial",  # Change font if needed
            bgcolor="rgba(0, 0, 0, 0.8)",  # Optional: Change background color for better contrast
            font_color="white"  # Optional: Change font color for readability
        )
    )

    with st.container():
        st.plotly_chart(fig, use_container_width=True)