import requests
import logging
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from funcs import load_data, find_longest_season, populate_heatmap_input

st.set_page_config(layout="wide")
streamlit_bg_color = "#0E1117"

logging.basicConfig(level=logging.DEBUG)

st.title(f'Plotting episode ratings')


data_load_state = st.text('Loading data...')

# 1. load all data and episode specific data
BASE_URL = 'https://api.tvmaze.com'
path = f'{BASE_URL}/shows/52?embed=episodes'

show_data, episodes_data = load_data(path)

# 2. get other metadata
show_name = show_data['name']
show_language = show_data['language']
show_status = show_data['status']
average_rating = show_data['rating']['average']

data_load_state.text("Loading data...done!")

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

st.subheader(f'📊 Plotting episode ratings for {show_name}')

#TODO - add check if episode_rating is all None, dont show viz, say dont have ratings for this :(
# print(df["episode_rating"].isna().sum())

# trace1 = go.Heatmap(
#     z=[[1 if np.isnan(rating) else np.nan for rating in row] for row in ratings_list],  # Use 1 for NaN cells
#     x=columns_plotly,  # Columns labels
#     y=rows_plotly,  # Rows labels
#     colorscale=[[0, "white"], [1, "white"]],  # NaN values are displayed as white
#     showscale=False,  # No color scale for NaN cells
#     hoverinfo="skip",  # Skip hover for NaN cells
# )

# bold_text = [[f"<b>{rating}</b>" for rating in row] for row in ratings_list]

# # Trace for valid ratings (Viridis color scale)
# trace2 = go.Heatmap(
#     z=ratings_list,  # Ratings with np.nan values
#     x=columns_plotly,  # Columns labels
#     y=rows_plotly,  # Rows labels
#     colorscale="Magma_r",  # Use the Viridis color scale for valid ratings
#     colorbar={"title": "Ratings"},  # Colorbar for ratings scale
#     text=episodes_name_list,
#     texttemplate= "<b>%{z}</b>", # Show episode names on hover
#     hovertemplate="%{text}<extra></extra>",  # Hover info
# )

# # trace2 = go.Heatmap(
# #     z=ratings_list,  # Ratings with np.nan values
# #     x=columns_plotly,  # Columns labels
# #     y=rows_plotly,  # Rows labels
# #     colorscale="Viridis",  # Use the Viridis color scale for valid ratings
# #     colorbar={"title": "Ratings"},  # Colorbar for ratings scale
# #     text=ratings_list,  # Show episode names on hover
# #     hovertemplate="Episode: %{text}<br>Rating: %{z}",  # Hover info
# #     texttemplate="%{text}",  # Display the text inside the cells
# #     textfont={"size": 16, "color": "white"}  # Customize text font and color
# # )

# # Combine both traces into data
# data = [trace1, trace2]

# # Layout settings
# layout = {
#     "title": f"Episode Ratings: {show_name} | Language: {show_language} | Show status: {show_status}) | Overall Rating: {average_rating}",    "xaxis": {"side": "top"},
#     "yaxis": dict(visible=True,autorange='reversed'),
#     "height": 800,  # Set desired plot height
#     "autosize": True,
# }

# # Create the figure and plot it
# fig = go.Figure(data=data, layout=layout)
# # fig = fig.update_traces(text=df.applymap(p.number_to_words).values)

# fig.show()

# streamlit version

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

# Add a container to avoid crowding
with st.container():
    st.plotly_chart(fig, use_container_width=True)