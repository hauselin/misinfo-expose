#%%

import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st
from PIL import Image

#%%


def get_data(screen_name):
    url = f"https://mescalc.p.rapidapi.com/account/{screen_name}"
    headers = {
        "X-RapidAPI-Host": st.secrets["host"],
        "X-RapidAPI-Key": st.secrets["key"],
    }
    return requests.request("GET", url, headers=headers).json()


#%% data for plotting

partydata = pd.DataFrame(
    {
        "party": ["Democrat", "Republican"],
        "value": [-1, 1],
        "label": ["", ""],
        "score": [0.0, 0.0],
    }
)


#%%

st.set_page_config(page_title="Misinformation exposure")

st.markdown("### How much misinformation are you exposed to?")

st.write("Mohsen Mosleh. App information and add citation etc.")

screen_name = st.text_input("Enter your Twitter username or ID to find out.")

#%%

if screen_name:
    if screen_name[0] == "@":
        screen_name = screen_name[1:]

    with st.spinner("Retrieving data..."):
        data = get_data(screen_name)

    if data.get("message") and data["message"].startswith("Cannot find information"):
        st.warning("Cannot find user. Please check your username or ID.")
    else:
        st.markdown(
            f"You entered **{data['twitter_screen_name']}** (ID: {data['twitter_user_id']})."
        )

        columns = st.columns(3)
        columns[0].metric(
            "Exposure", value=data["misinfo_exposure_score"], delta="1.2%"
        )
        columns[1].metric(
            "Weighted exposure",
            value=data["misinfo_exposure_score_weighted_numtweets"],
            delta="-1.2%",
        )
        columns[2].metric("Partisanship", value=data["partisan_score"], delta="1.2%")

        #%% figures

        st.write("add figures below")

        # partisanship
        st.markdown(
            "<h5 style='text-align: center;'>Partisanship</h1>",
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        partydata["score"] = data["partisan_score"]
        bar = (
            alt.Chart(partydata)
            .mark_bar()
            .encode(
                x=alt.X("value", title="Democratic - Republican"),
                y=alt.Y("label", title=""),
                color=alt.Color(
                    field="party",
                    scale=alt.Scale(range=["#234898", "#d22532"], interpolate="hsl"),
                    legend=None,
                ),
            )
            # .properties(title="Partisanship")
        )

        tick = (
            alt.Chart(partydata)
            .mark_tick(
                color="orange",
                thickness=4,
                size=34,
            )
            .encode(x="score", y="label", tooltip=["score"])
            .interactive()
        )
        plot_party = bar + tick
        plot_party.configure_title(fontSize=13)

        # img_dem = Image.open("img/dem_repub.png")
        # col2.image(img_dem, use_column_width=True)
        col2.altair_chart(plot_party, use_container_width=True)

        source = pd.DataFrame({"category": [1, 2], "value": [1, 2]})
        c1 = (
            alt.Chart(source)
            .mark_arc(outerRadius=100)
            .encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color=alt.Color(
                    field="category",
                    type="nominal",
                    scale=alt.Scale(range=["#09ab3b", "#ff4141"]),
                    legend=None,
                ),
            )
        )
        st.altair_chart(c1, use_container_width=True)

        st.markdown(
            f"The estimates above are based on these **{data['num_following']}** users **{data['twitter_screen_name'].lower()}** follows:"
        )
        st.json(data["following"])

    # st.write(data)


#%%
