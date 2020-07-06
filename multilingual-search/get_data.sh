#!/bin/bash


DATA_DIR=/tmp/jina/multilingual
mkdir -p ${DATA_DIR}

echo "- Downloading Laser model related files"
python -m laserembeddings download-models ${DATA_DIR}

echo "- Downloading WMT data"
wget --directory-prefix=${DATA_DIR} -q http://www.statmt.org/wmt13/dev.tgz

echo "- Extracting file to ${DATA_DIR}"
tar -xf ${DATA_DIR}/dev.tgz -C ${DATA_DIR}

# removing files that are not needed
rm ${DATA_DIR}/dev/*.sgm 
rm ${DATA_DIR}/dev/newssyscomb* 

# renaming 2008 files to the right format
for x in ${DATA_DIR}/dev/news-test*; do mv "$x" "`echo $x | sed 's/-//'`"; done
