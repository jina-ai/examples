#!/bin/sh
DATASET="noxmoon/chinese-official-daily-news-since-2016"
ARCHIVE_FILE="chinese-official-daily-news-since-2016.zip"
DATA_FILE="chinese_news.csv"
DATA_DIR="data"
COL_NAME="headline"
LINES=3000
OUTPUT_FILE="headlines.txt"

if [ -d ${DATA_DIR} ]; then
  echo ${DATA_DIR}' exists, please remove it before running the script'
  exit 1
fi

echo "Creating dir"
mkdir -p ${DATA_DIR}
cd ${DATA_DIR}
kaggle datasets download -d ${DATASET}
unzip ${ARCHIVE_FILE}

echo "Deleting original dataset archive"
rm -f ${ARCHIVE_FILE}

echo "Extracting, cutting, shuffling data"
awk  -v col=$COL_NAME -F "\"*,\"*" '{print $COL_NAME}' $DATA_FILE | shuf -n 3000 > ${OUTPUT_FILE}

