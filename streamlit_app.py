#%%

import base64
from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import requests
import streamlit as st

#%%


def get_data(screen_name):
    url = f"https://mescalc.p.rapidapi.com/account/{screen_name.lower()}"
    headers = {
        "X-RapidAPI-Host": st.secrets["host"],
        "X-RapidAPI-Key": st.secrets["key"],
    }
    return requests.request("GET", url, headers=headers).json()


# https://stackoverflow.com/questions/70932538/how-to-center-the-title-and-an-image-in-streamlit
def img_to_bytes(img_path):
    img_bytes = Path(img_path).read_bytes()
    return base64.b64encode(img_bytes).decode()


def img_to_html(img_path):
    return (
        f"<img src='data:image/png;base64,{img_to_bytes(img_path)}' class='img-fluid'>"
    )


def percent_delta(misinfo, partisan):
    misinfo = np.float_(misinfo)
    partisan = np.float_(partisan)
    misinfo_mean = 0.51
    partisan_mean = -0.352 + 1  # rescale to [0, 1], original was [-1, 1]
    follower_mean = 4.65

    partisan += 1
    misinfo_delta = misinfo - misinfo_mean
    partisan_delta = partisan - partisan_mean

    return np.round(misinfo_delta / misinfo_mean * 100, 2), np.round(
        partisan_delta / partisan_mean * 100, 2
    )


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

st.markdown(
    "Citation: *Measuring exposure to misinformation from political elites on Twitter. Mosleh, M. & Rand, D.G., Nature Communications, 2022.*"
)

st.markdown(
    "**Misinformation exposure** scores range from 0 (not exposed to any misinformation) to 1 (exposed to a lot of misinformation). **Partisanship** scores range from -1 (follow mostly Democrats) to 1 (follow mostly Republicans)."
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
        print(data)
        st.markdown(
            f"Scores for **{data['twitter_screen_name']}** (ID: {data['twitter_user_id']}) are shown below. You can also see how much (%) the scores deviate from the mean. The vertical lines in the figures show your scores."
        )

        st.markdown("#### ")

        percent_delta_misinfo, percent_delta_partisan = percent_delta(
            data["misinfo_exposure_score"], data["partisan_score"]
        )

        delta = None if np.isnan(percent_delta_misinfo) else f"{percent_delta_misinfo}%"
        columns = st.columns(3)
        columns[0].metric(
            "Exposure",
            value=data["misinfo_exposure_score"],
            delta=delta,
            help="Misinformation exposure score (min/max: 0/1)",
        )
        columns[1].metric(
            "Weighted exposure",
            value=data["misinfo_exposure_score_weighted_numtweets"],
            help="Misinformation exposure score weighted by number of tweets (min/max: 0/1)",
        )
        delta = (
            None if np.isnan(percent_delta_partisan) else f"{percent_delta_partisan}%"
        )
        columns[2].metric(
            "Partisanship",
            value=data["partisan_score"],
            delta=delta,
            help="Higher scores: more Republican (min/max: -1/1)",
        )

        #%% figures

        st.markdown("# ")

        # misinfo exposure
        st.markdown(
            "<h5 style='text-align: center;'>Exposure to misinformation</h1>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 6, 1])
        misinfodata["score"] = data["misinfo_exposure_score"]
        axis_labels = "datum.label == 0 ? ['0.0','Low']: datum.label == 1.0 ? ['1.0','High']: datum.label"
        bar = (
            alt.Chart(misinfodata)
            .mark_bar()
            .encode(
                x=alt.X("value", title="", axis=alt.Axis(labelExpr=axis_labels)),
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
                thickness=3,
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
                color="yellow",
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

        # partisanship
        st.markdown(
            "<h5 style='text-align: center;'>Partisanship</h1>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='text-align: center; color: grey;'>"
            + img_to_html("img/dem_repub_small.png")
            + "</p>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 6, 1])
        partydata["score"] = data["partisan_score"]
        axis_labels = "datum.label == -1.0 ? ['—1.0','Democrat']: datum.label == 1.0 ? ['1.0','Republican']: datum.label"
        bar = (
            alt.Chart(partydata)
            .mark_bar()
            .encode(
                x=alt.X("value", title="", axis=alt.Axis(labelExpr=axis_labels)),
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
                color="yellow",
                thickness=5,
                size=34,
            )
            .encode(x="score", y="label", tooltip=["score"])
        )
        plot_party = bar + tick
        plot_party.configure_title(fontSize=13)
        col2.altair_chart(plot_party, use_container_width=True)

        if int(data["num_following"]) > 1:
            st.markdown(
                f"The estimates above are based on these **{data['num_following']}** users **{data['twitter_screen_name'].lower()}** follows:"
            )
        else:
            st.markdown(
                f"The estimates above are based on this user **{data['twitter_screen_name'].lower()}** follows:"
            )
        st.json(data["following"])

    # st.write(data)


#%%
