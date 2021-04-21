#!/bin/bash

TEST_DATA_DIR=data/

rm -rf ${TEST_DATA_DIR} && \
pip install gdown && \
gdown https://drive.google.com/uc\?id\=1j0Z79PtHGDfzmb-0kdY3D7vP4-I3mJ2P && \
unzip fashion200k.zip && \
rm fashion200k.zip && \
mkdir -p ${TEST_DATA_DIR} && \
mv women ${TEST_DATA_DIR}/images && \
mv image_urls.txt ${TEST_DATA_DIR}/image_urls.txt && \
mv labels ${TEST_DATA_DIR}/labels && \
mv detection ${TEST_DATA_DIR}/detection && \
rm -rf workspace && \
python app.py -t index | tee metrics.txt && \
python app.py -t query | tee >> metrics.txt && \
rm -rf ${TEST_DATA_DIR}
