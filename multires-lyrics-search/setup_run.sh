#!/bin/bash
rm -rf workspace && \
python app.py index | tee metrics.txt