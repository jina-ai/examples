__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import streamlit as st
from util import get_results, render_results


st.title("South Park Search")
st.write("Who said what?")

st.sidebar.title("Search with Jina")
query = st.sidebar.text_input("What do you wish to search?")
top_k = st.sidebar.slider("Top K", min_value=1, max_value=20, value=10)

if st.sidebar.button("Search"):
    results = get_results(query=query, top_k=top_k)
    st.balloons()
    st.markdown(render_results(results))
