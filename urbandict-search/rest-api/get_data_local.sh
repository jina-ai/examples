#!/bin/sh
if [ "$#" -ne 1 ]; then
  echo 'bash ./get_data_local.sh PATH_TO_DATA_FILE.tgz'
  exit 1
fi

DATA_PATH=$1
TEST_WORKDIR=/tmp
cp ${DATA_PATH} ${TEST_WORKDIR}
python prepare_data.py
