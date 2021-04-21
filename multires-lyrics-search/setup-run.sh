#!/bin/bash
rm -rf workspace && \
python app.py index | tee metrics.txt && \
python app.py search | tee >> metrics.txt
