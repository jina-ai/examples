#!/bin/bash

TEST_DATA_DIR=data/

rm -rf ${TEST_DATA_DIR} && \
python ../.github/util/pull_dataset.py -d multimodal-search-tirg/fashion200k.zip -p ../ && \
unzip -o fashion200k.zip && \
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
