#%%

import requests
import streamlit as st

#%%


def get_data(screen_name):
    url = f"https://mescalc.p.rapidapi.com/account/{screen_name}"
    headers = {
        "X-RapidAPI-Host": st.secrets["host"],
        "X-RapidAPI-Key": st.secrets["key"],
    }
    return requests.request("GET", url, headers=headers)


#%%

st.title("Misinformation exposure")
st.write("How much misinformation are you exposed to?")

screen_name = st.text_input("Enter your Twitter username or ID")

#%%

if screen_name:
    data = get_data(screen_name).json()

    st.write("Username and ID", data["twitter_user_id"])
    st.write(data)

#%%
