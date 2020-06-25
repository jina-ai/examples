#!/bin/sh
if [ "$#" -ne 1 ]; then
  echo 'bash ./get_data_local.sh PATH_TO_DATA_FILE.tgz'
  exit 1
fi

DATA_PATH=$1
TEST_WORKDIR=/data
mkdir -p ${TEST_WORKDIR}
cd ${TEST_WORKDIR}
cp ${DATA_PATH} 17flowers.tgz
tar zxf 17flowers.tgz
