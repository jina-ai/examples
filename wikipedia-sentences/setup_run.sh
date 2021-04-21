#!/bin/bash
#rm -rf data && \
#bash get_data.sh && \
rm -rf workspace && \
export JINA_DATA_FILE='data/input.txt' && \
python app.py -t index -n 500 | tee metrics.txt