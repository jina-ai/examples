#pip install speedtest-cli
#run it as streamlit run main.py

import speedtest
import streamlit as st
speedt = speedtest.Speedtest()

page_bg_img = '''
<style>
body {
background-image: url("https://images.unsplash.com/photo-1534078362425-387ae9668c17");
background-size: cover;
}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("Internet Speed Calculator!")
download = round(speedt.download()*0.000000125,2)
upload = round(speedt.upload()*0.000000125,2)
ping = round(speedt.results.ping,2)
st.write("Your download speed is: " + str(download) + " MB/s")
st.write("Your upload speed is: " + str(upload) + " MB/s")
st.write("Your ping is: " + str(ping))
