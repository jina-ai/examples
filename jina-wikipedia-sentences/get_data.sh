#!/bin/sh
DATASET="mikeortman/wikipedia-sentences"
DATA_DIR="data"
LINES=3000

if [ -d ${DATA_DIR} ]; then
  echo ${DATA_DIR}' exists, please remove it before running the script'
  exit 1
fi

mkdir -p ${DATA_DIR}
cd ${DATA_DIR}
kaggle datasets download -d ${DATASET}
unzip wikipedia-sentences.zip
shuf wikisent2.txt > input.txt
rm -f wikisent2.txt
