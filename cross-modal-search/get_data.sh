#!/bin/sh
DATASET="adityajn105/flickr8k"
DATA_DIR="data/f8k"

if [ -d ${DATA_DIR} ]; then
  echo ${DATA_DIR}' exists, please remove it before running the script'
  exit 1
fi

mkdir -p ${DATA_DIR} && \
kaggle datasets download -d ${DATASET} && \
unzip -q flickr8k.zip && \
rm flickr8k.zip && \
mv Images data/f8k/images && \
mv captions.txt data/f8k/captions.txt