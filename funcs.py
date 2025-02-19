import requests
import pandas as pd
import streamlit as st

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