#!/bin/sh
DATASET="adityajn105/flickr8k"
DATA_DIR="data/f8k"

if [ -d ${DATA_DIR} ]; then
  echo ${DATA_DIR}' exists, please remove it before running the script'
  exit 1
fi

mkdir -p ${DATA_DIR}
kaggle datasets download -d ${DATASET}
