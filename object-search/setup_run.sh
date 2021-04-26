#!/bin/bash
# these scripts will contain everything that needs to be run before the example
# downloading data, model, preprocessing etc.
rm -rf workspace
python app.py -t index | tee metrics.txt
