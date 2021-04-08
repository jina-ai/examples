#!/bin/bash
pip install --upgrade youtube_dl && \
sudo apt-get install ffmpeg && \
rm -rf models && \
rm -rf data && \
bash download_model.sh && \
bash download_data.sh && \
rm -rf workspace && \
python app.py -t index | tee metrics.txt