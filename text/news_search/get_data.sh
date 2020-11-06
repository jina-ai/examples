#!/bin/sh
TEST_DATA_DIR=$1
if [ "$#" -ne 1 ]; then
  echo "bash ./get_data.sh [TEST_DATA_DIR]"
  exit 1
fi

if [ -d ${TEST_DATA_DIR} ]; then
  rm -r ${TEST_DATA_DIR}
fi

kaggle datasets download -d shineucc/bbc-news-dataset
unzip bbc-news-dataset.zip
cp 'BBC news dataset.csv' bbc_news.csv
rm 'BBC news dataset.csv'
rm bbc-news-dataset.zip

mkdir -p ${TEST_DATA_DIR}

mv bbc_news.csv ${TEST_DATA_DIR}
