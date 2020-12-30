#!/bin/sh
TEST_DATA_DIR=$1
if [ "$#" -ne 1 ]; then
  echo "bash ./get_data.sh [TEST_DATA_DIR]"
  exit 1
fi

if [ -d ${TEST_DATA_DIR} ]; then
  rm -r ${TEST_DATA_DIR}
fi

kaggle datasets download -d mayukh18/fashion200k-dataset
unzip fashion200k-dataset.zip
rm fashion200k-dataset.zip

mkdir -p ${TEST_DATA_DIR}

mv women ${TEST_DATA_DIR}/images
mv image_urls.txt ${TEST_DATA_DIR}/image_urls.txt
mv labels ${TEST_DATA_DIR}/labels
mv detection ${TEST_DATA_DIR}/detection

