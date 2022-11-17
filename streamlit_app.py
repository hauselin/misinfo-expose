#%%

import requests
import streamlit as st
import json

#%%


def get_data(screen_name):
    url = f"https://mescalc.p.rapidapi.com/account/{screen_name}"
    headers = {
        "X-RapidAPI-Host": st.secrets["host"],
        "X-RapidAPI-Key": st.secrets["key"],
    }
    return requests.request("GET", url, headers=headers)


#%%

st.markdown("### How much misinformation are you exposed to?")

screen_name = st.text_input("Enter your Twitter username or ID to find out.")

#%%

if screen_name:
    data = get_data(screen_name).json()

    if data.get("message") and data["message"].startswith("Cannot find information"):
        st.write("Cannot find user. Please check your username or ID.")
    else:
        st.markdown(
            f"You entered **{data['twitter_screen_name']}** (ID: {data['twitter_user_id']})."
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("Exposure", value=data["misinfo_exposure_score"], delta="1.2%")
        col2.metric(
            "Weighted exposure",
            value=data["misinfo_exposure_score_weighted_numtweets"],
            delta="-1.2%",
        )
        col3.metric("Partisanship", value=data["partisan_score"], delta="1.2%")

        st.markdown(
            f"The estimates above are based on these **{data['num_following']}** users **{data['twitter_screen_name'].lower()}** follows:"
        )
        st.json(data["following"])

    # st.write(data)

#%%
