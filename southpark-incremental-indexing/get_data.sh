#!/bin/sh
TEST_DATA_DIR=$1
if [ "$#" -ne 1 ]; then
  echo "bash ./get_data.sh [TEST_DATA_DIR]"
  exit 1
fi

if [ -d ${TEST_DATA_DIR} ]; then
  echo ${TEST_DATA_DIR}' exists, please remove it before running the script'
  exit 1
fi

mkdir -p ${TEST_DATA_DIR}
git clone https://github.com/BobAdamsEE/SouthParkData.git $TEST_DATA_DIR
python prepare_data.py ${TEST_DATA_DIR}
