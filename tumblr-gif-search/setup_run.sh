#!/bin/bash
python gif_download.py -l 500 && \
rm -rf workspace && \
python app.py -t index | tee metrics.txt