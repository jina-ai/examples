__copyright__ = "Copyright (c) 2020 Jina AI Limited. All rights reserved."
__license__ = "Apache-2.0"

import streamlit as st
from PIL import Image
from util import Getter, Defaults, Renderer, Encoder
from streamlit_drawable_canvas import st_canvas


st.title("Jina Search")
media_option = ["Text", "Image", "Draw"]

st.sidebar.title("Options")
media_select = st.sidebar.selectbox(label="Media", options=media_option)
endpoint = st.sidebar.text_input("Endpoint", value=Defaults.endpoint)
top_k = st.sidebar.slider("Top K", min_value=1, max_value=20, value=10)

if media_select == "Text":
    query = st.text_input("What do you wish to search?", value=Defaults.text_query)
elif media_select == "Image":
    query = st.file_uploader("File")
elif media_select == "Draw":
    st.sidebar.header("Drawing Options")
    stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
    stroke_color = st.sidebar.color_picker("Stroke color hex: ")
    bg_color = st.sidebar.color_picker("Background color hex: ", "#ffffff")
    bg_image = st.sidebar.file_uploader("Background image:", type=["png", "jpg"])
    drawing_mode = st.sidebar.selectbox(
        "Drawing tool:", ("freedraw", "line", "rect", "circle", "transform")
    )

    data = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",  # Fixed fill color with some opacity
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="" if bg_image else bg_color,
        background_image=Image.open(bg_image) if bg_image else None,
        update_streamlit=True,
        width=400,
        height=400,
        drawing_mode=drawing_mode,
        key="canvas",
    )

if st.button("Search"):
    if media_select == "Text":
        results = Getter.text(query=query, top_k=top_k, endpoint=endpoint)
        content = results
        st.markdown(Renderer.text(content))
    elif media_select == "Image" or media_select == "Draw":
        if media_select == "Image":
            encoded_query = Encoder.img_base64(query.read())
        elif media_select == "Draw":
            encoded_query = Encoder.canvas_to_base64(data)
        results = Getter.images(endpoint=endpoint, query=encoded_query, top_k=top_k)
        html = Renderer.images(results)
        st.write(html, unsafe_allow_html=True)
    st.balloons()
