#!/bin/bash

TEST_DATA_DIR=data/

rm -rf ${TEST_DATA_DIR} && \
mkdir -p ${TEST_DATA_DIR}/f8k/images && \
pip install gdown && \
gdown https://drive.google.com/uc\?id\=16HLqP-0opQegbrPA-3BkXRUQycoVMcfK && \
unzip f8k.zip -d ${TEST_DATA_DIR} && \
rm f8k.zip && \
mv ${TEST_DATA_DIR}/Images/* ${TEST_DATA_DIR}/f8k/images && \
mv ${TEST_DATA_DIR}/captions.txt data/f8k/captions.txt && \
rm -rf workspace && \
python app.py -t index | tee metrics.txt && \
rm -rf ${TEST_DATA_DIR}