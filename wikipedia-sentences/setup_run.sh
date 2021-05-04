#!/bin/bash
DATA_DIR='data'
DATA_FILE='input.txt'

if [ ! -f "$DATA_DIR/$DATA_FILE" ]; then
  echo 'no data file found. starting download, this may take a while...'
  python ../util/pull_dataset.py -d ${DATA_FILE} -p ${DATA_DIR}
fi

rm -rf workspace && \
export JINA_DATA_FILE="$DATA_DIR/$DATA_FILE" && \
python app.py -t index -n 5000 | tee metrics.txt && \
python app.py -t query <<< 'some text from stdin' | tee >> metrics.txt