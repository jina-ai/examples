#!/bin/bash
rm -rf workspace && \
python app.py -t index | tee metrics.txt