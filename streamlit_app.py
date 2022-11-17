#%%

import altair as alt
import numpy as np
import requests
import streamlit as st
import pandas as pd

#%%


def get_data(screen_name):
    url = f"https://mescalc.p.rapidapi.com/account/{screen_name}"
    headers = {
        "X-RapidAPI-Host": st.secrets["host"],
        "X-RapidAPI-Key": st.secrets["key"],
    }
    return requests.request("GET", url, headers=headers).json()


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

        st.write("add figures below")
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
