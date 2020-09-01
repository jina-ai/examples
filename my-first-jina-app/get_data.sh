#!/bin/sh
WORKDIR=./data
mkdir -p ${WORKDIR}
wget -P $WORKDIR https://github.com/alexcg1/ml-datasets/raw/master/nlp/startrek/startrek_tng.csv
export DATA_PATH='data/startrek_tng.csv'