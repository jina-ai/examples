#!/bin/bash
rm -rf data && \
rm -rf pretrained && \
./get_data.sh && \
./download.sh && \
rm -rf workspace && \
python app.py -t index -n 10000 | tee metrics.txt