#!/bin/sh
DATA_DIR=data
if [ -d ${DATA_DIR} ]; then
  echo ${DATA_DIR}' exists, please remove it before running the script'
  exit 1
fi

mkdir -p ${DATA_DIR}

wget -P ${DATA_DIR} https://veekun.com/static/pokedex/downloads/generation-1.tar.gz
wget -P ${DATA_DIR} https://veekun.com/static/pokedex/downloads/generation-2.tar.gz
wget -P ${DATA_DIR} https://veekun.com/static/pokedex/downloads/generation-3.tar.gz
wget -P ${DATA_DIR} https://veekun.com/static/pokedex/downloads/generation-4.tar.gz
wget -P ${DATA_DIR} https://veekun.com/static/pokedex/downloads/generation-5.tar.gz

cd ${DATA_DIR}

for i in *.tar.gz; do tar -zxvf ${i}; rm -f ${i}; done

cd ..
