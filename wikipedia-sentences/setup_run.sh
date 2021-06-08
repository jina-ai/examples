#!/bin/bash
EXAMPLE='wikipedia-sentences'
DATA_DIR='data'
DATA_FILE='input.zip'

rm -rf ${DATA_DIR} && \
mkdir -p ${DATA_DIR} && \
python ../.github/util/pull_dataset.py -d ${EXAMPLE}/${DATA_FILE} -p ../ && \
unzip ${DATA_FILE} -d ${DATA_DIR} && \
rm ${DATA_FILE} && \
rm -rf workspace && \
export JINA_DATA_FILE="$DATA_DIR/input.txt" && \
python app.py -t index -n 10000 | tee metrics.txt && \
python app.py -t query <<< 'some text from stdin' | tee >> metrics.txt
rm -rf ${DATA_DIR}