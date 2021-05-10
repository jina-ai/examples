#!/bin/bash
rm -rf workspace && \
python app.py -t index | tee metrics.txt && \
python app.py -t query <<< 'some text from stdin' | tee >> metrics.txt