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


def lower_or_higher(delta):
    if delta is None:
        return delta
    if delta[0] == "-":
        delta = f"{delta} lower than average"
    else:
        delta = f"{delta} higher than average"
    return delta


#%% data

df_falsity = pd.read_csv("data/falsity_scores.csv")
df_misinfo_dist = pd.read_csv("data/dist_simulated.csv")


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


#%% app set up

st.set_page_config(page_title="Misinformation exposure")

# remove footer txt
# https://discuss.streamlit.io/t/remove-made-with-streamlit-from-bottom-of-app/1370/2
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

#%% main text

st.markdown("### 🐥 How much misinformation are you exposed to? 🐥")

st.markdown(
    "Citation: *[Measuring exposure to misinformation from political elites on Twitter](https://psyarxiv.com/ye3pf). Mosleh, M. & Rand, D.G., Nature Communications, 2022*. See Tweet thread [here](https://twitter.com/_mohsen_m/status/1482072249427505152) 🐦"
)

st.markdown(
    "**Misinformation exposure** scores measure how much the politicians and public organizations you follow tend to lie (based on fact-checking their claims by [PolitiFact](https://www.politifact.com/)). These scores go from 0 (none of the fact-checked claims by politicians and public figures you follow are false) to 1 (all of the fact-checked claims by politicians and public organizations you follow are false). "
)

st.markdown(
    "**Partisanship** scores measure how much you tend to follow politicians from the left versus right side of the political spectrum. These scores go from -1 (follow only left-leaning accounts) to 1 (follow only right-leaning accounts)."
)

st.markdown(
    "You can also use our [API](https://github.com/mmosleh/minfo-exposure) to get the scores. Source code for this app is available [here](https://github.com/hauselin/misinfo-expose/tree/main)."
)

screen_name = st.text_input("Enter your Twitter username or ID to find out.")

#%% results

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
            f"Scores for **{data['twitter_screen_name']}** (ID: {data['twitter_user_id']}) are shown below."
        )

        st.markdown("##### ")

        percent_delta_misinfo, percent_delta_partisan = percent_delta(
            data["misinfo_exposure_score"], data["partisan_score"]
        )

        delta = None if np.isnan(percent_delta_misinfo) else f"{percent_delta_misinfo}%"
        delta = lower_or_higher(delta)
        columns = st.columns([1, 1])
        columns[0].metric(
            "Misinformation exposure",
            value=data["misinfo_exposure_score_weighted_numtweets"],
            help="Misinformation exposure score weighted by number of tweets (min/max: 0/1)",
            delta=delta,
            delta_color="off",
        )
        delta = (
            None if np.isnan(percent_delta_partisan) else f"{percent_delta_partisan}%"
        )
        delta = lower_or_higher(delta)
        columns[1].metric(
            "Partisanship",
            value=data["partisan_score"],
            delta=delta,
            help="Higher scores: more Republican (min/max: -1/1)",
            delta_color="off",
        )

        #%% figures

        st.markdown("# ")

        # misinfo exposure
        st.markdown(
            "<h5 style='text-align: center;'>Misinformation exposure</h1>",
            unsafe_allow_html=True,
        )

        if data["misinfo_exposure_score_weighted_numtweets"] is None:
            st.markdown(
                "<div style='text-align: center;'>No misinformation exposure score is available for this user.</div><br>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='text-align: center;'>The <b><span style='color: #91e5f6;'>vertical line</span></b> is where you are in relation to others.</div>",
                unsafe_allow_html=True,
            )

        col1, col2, col3 = st.columns([0.6, 6.4, 1])
        axis_labels = "''"

        col1, col2, col3 = st.columns([1, 6, 1])
        axis_labels = "datum.label == 0 ? ['0.0','Low']: datum.label == 1.0 ? ['1.0','High']: datum.label"
        dens = (
            alt.Chart(df_misinfo_dist)
            .transform_density("value", as_=["value", "density"], extent=[0, 1])
            .mark_area(color="#d8dbe2", opacity=0.8)
            .encode(
                x=alt.X("value:Q", title="", axis=alt.Axis(labelExpr=axis_labels)),
                y=alt.Y("density:Q", title="", axis=alt.Axis(labels=False, tickSize=0)),
                tooltip=["value"],
            )
        )

        misinfodata["score"] = data["misinfo_exposure_score"]
        misinfodata["score_weighted"] = data[
            "misinfo_exposure_score_weighted_numtweets"
        ]
        rule = (
            alt.Chart(misinfodata)
            .mark_rule(color="#91e5f6", size=3)
            .encode(x="score_weighted:Q", tooltip=["score_weighted"])
        )

        if data["misinfo_exposure_score_weighted_numtweets"] is not None:
            plot_misinfoexpose = dens + rule
        else:
            plot_misinfoexpose = dens
        plot_misinfoexpose = (
            plot_misinfoexpose.configure_title(fontSize=13)
            .configure_axis(grid=False, domain=False)
            .configure_view(strokeWidth=0)
        )
        col2.altair_chart(plot_misinfoexpose, use_container_width=True)

        # partisanship
        st.markdown(
            "<h5 style='text-align: center;'>Partisanship</h1>",
            unsafe_allow_html=True,
        )

        if data["partisan_score"] is None:
            st.markdown(
                "<div style='text-align: center;'>No partisanship score is available for this user.</div><br>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<p style='text-align: center; color: grey;'>"
            + img_to_html("img/dem_repub_small_nobg.png")
            + "</p>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns([1, 6, 1])
        partydata["score"] = data["partisan_score"]
        axis_labels = "datum.value == -1.0 ? ['-1.0','Democrat']: datum.value == 1.0 ? ['1.0','Republican']: datum.value == 0.0 ? ['0.0']: ''"

        bar = (
            alt.Chart(partydata)
            .mark_bar()
            .encode(
                x=alt.X(
                    "value",
                    title="",
                    axis=alt.Axis(labelExpr=axis_labels),
                ),
                y=alt.Y("label", title=""),
                color=alt.Color(
                    field="party",
                    scale=alt.Scale(range=["#34459d", "#f50e02"], interpolate="hsl"),
                    legend=None,
                ),
                tooltip=["party"],
            )
        )

        tick = (
            alt.Chart(partydata)
            .mark_tick(color="#91e5f6", thickness=5, size=34)
            .encode(x="score", y="label", tooltip=["score"])
        )
        plot_party = bar + tick if data["partisan_score"] is not None else bar
        plot_party.configure_title(fontSize=13)
        col2.altair_chart(plot_party, use_container_width=True)

        if int(data["num_following"]) > 1:
            st.markdown(
                f"The estimates above are based on these **{data['num_following']}** users **{data['twitter_screen_name'].lower()}** follows. Falsity scores for the elites are also shown. "
            )
        else:
            st.markdown(
                f"The estimates above are based on this user **{data['twitter_screen_name'].lower()}** follows. The elite's falsity score is also shown."
            )

        # show dataframe of elites and falsity scores
        cols = st.columns([1, 2, 1])
        df = pd.DataFrame(data["following"])
        df.columns = ["elite_account"]
        df = (
            pd.merge(df, df_falsity, on="elite_account", how="left")
            .sort_values("falsity_score", ascending=False)[
                ["elite_account", "falsity_score"]
            ]
            .reset_index(drop=True)
        )
        df.columns = ["Elite", "Falsity score"]
        df.index = df.index + 1
        # https://discuss.streamlit.io/t/how-to-format-float-values-to-2-decimal-place-in-a-dataframe-except-one-column-of-the-dataframe/3619/3
        cols[1].dataframe(
            df.style.format(subset=["Falsity score"], formatter="{:.3f}"),
            use_container_width=True,
        )

        # st.write(data)


#%%
