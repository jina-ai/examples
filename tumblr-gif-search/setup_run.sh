#!/bin/bash
rm -rf data/*.gif && \
python gif_download.py -l 1000 && \
rm -rf workspace && \
python app.py -t index | tee metrics.txt