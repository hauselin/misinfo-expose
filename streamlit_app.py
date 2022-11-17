#%%

import altair as alt
import pandas as pd
import requests
import streamlit as st
from PIL import Image

#%%


def get_data(screen_name):
    url = f"https://mescalc.p.rapidapi.com/account/{screen_name.lower()}"
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

misinfodata = pd.DataFrame(
    {
        "exposure": ["low", "high"],
        "value": [0, 1],
        "label": ["", ""],
        "score": [0.5, 0.5],
    }
)


#%%

st.set_page_config(page_title="Misinformation exposure")

st.markdown("### How much misinformation are you exposed to?")

st.write("Mohsen Mosleh. App information and add citation etc.")

st.write(
    "Measuring exposure to misinformation from political elites on Twitter Mosleh, M, Rand G. R, Nature Communications 2022"
)

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
        columns[0].metric("Partisanship", value=data["partisan_score"], delta="1.2%")
        columns[1].metric(
            "Exposure", value=data["misinfo_exposure_score"], delta="1.2%"
        )
        columns[2].metric(
            "Weighted exposure",
            value=data["misinfo_exposure_score_weighted_numtweets"],
            delta="-1.2%",
        )

        #%% figures

        # partisanship
        st.markdown(
            "<h5 style='text-align: center;'>Partisanship</h1>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 6, 1])
        partydata["score"] = data["partisan_score"]
        bar = (
            alt.Chart(partydata)
            .mark_bar()
            .encode(
                x=alt.X("value", title="Democratic - Republican"),
                y=alt.Y("label", title=""),
                color=alt.Color(
                    field="party",
                    scale=alt.Scale(range=["#34459d", "#f50e02"], interpolate="hsl"),
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
        )
        plot_party = bar + tick
        plot_party.configure_title(fontSize=13)

        img_dem = Image.open("img/dem.png")
        col1.image(img_dem, use_column_width=True)
        img_rep = Image.open("img/repub.png")
        col3.image(img_rep, use_column_width=True)

        col2.altair_chart(plot_party, use_container_width=True)

        # misinfo exposure
        st.markdown(
            "<h5 style='text-align: center;'>Exposure to misinformation</h1>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 6, 1])
        misinfodata["score"] = data["misinfo_exposure_score"]
        bar = (
            alt.Chart(misinfodata)
            .mark_bar()
            .encode(
                x=alt.X("value", title="Low - High"),
                y=alt.Y("label", title=""),
                color=alt.Color(
                    field="exposure",
                    legend=None,
                ),
            )
        )

        tick = (
            alt.Chart(misinfodata)
            .mark_tick(
                color="orange",
                thickness=2,
                size=34,
            )
            .encode(x="score", y="label", tooltip=["score"])
        )

        misinfodata["score_weighted"] = data[
            "misinfo_exposure_score_weighted_numtweets"
        ]
        tick_weight = (
            alt.Chart(misinfodata)
            .mark_tick(
                color="white",
                thickness=2,
                size=34,
            )
            .encode(x="score_weighted", y="label", tooltip=["score_weighted"])
        )

        plot_misinfoexpose = bar + tick + tick_weight
        plot_misinfoexpose.configure_title(fontSize=13)

        # img_dem = Image.open("img/dem_repub.png")
        # col2.image(img_dem, use_column_width=True)
        col2.altair_chart(plot_misinfoexpose, use_container_width=True)

        st.markdown(
            f"The estimates above are based on these **{data['num_following']}** users **{data['twitter_screen_name'].lower()}** follows:"
        )
        st.json(data["following"])

    # st.write(data)


#%%
