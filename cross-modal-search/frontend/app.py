import streamlit as st
import requests
from config import endpoint
import base64


headers = {"Content-Type": "application/json"}

def search_by_text(query: str, endpoint: str, top_k: int) -> dict:
    """search_by_text.

    :param query:
    :type query: str
    :param endpoint:
    :type endpoint: str
    :param top_k:
    :type top_k: int
    :rtype: dict
    """
    data = '{"top_k":' + str(top_k) + ',"mode":"search","data":["' + query + '"]}'

    response = requests.post(endpoint, headers=headers, data=data)
    content = response.json()

    matches = content["data"]["docs"][0]["matches"]

    return matches

query = st.text_input("", value="Search query")
button = st.button("Go go go")

if button:
    matches = search_by_text(query, endpoint=endpoint, top_k=1)
    # st.json(matches)
    
    for match in matches:
        uri = match["tags"]["uri"]
        st.write(uri)
        st.markdown(f"<img src='{uri}'>", unsafe_allow_html=True)
        # st.json(match)
