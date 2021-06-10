#!/bin/bash
EXAMPLE='object-search'
DATA_DIR='data'
DATA_FILE='f8k.zip'

rm -rf ${DATA_DIR} && \
mkdir -p ${DATA_DIR}/f8k/images && \
python ../.github/util/pull_dataset.py -d ${EXAMPLE}/${DATA_FILE} -p ../ && \
unzip ${DATA_FILE} -d ${DATA_DIR} && \
rm ${DATA_FILE} && \
mv ${DATA_DIR}/Images/* ${DATA_DIR}/f8k/images && \
rm -rf workspace && \
export JINA_DATA_FILE="$DATA_DIR/f8k/images/*.jpg" && \
python app.py -t index -n 5000 | tee metrics.txt && \
rm -rf ${DATA_DIR}