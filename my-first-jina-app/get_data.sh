#!/bin/sh
WORKDIR=./data
mkdir -p ${WORKDIR}
wget -P $WORKDIR/raw https://github.com/alexcg1/ml-datasets/raw/master/nlp/startrek/startrek_tng.csv
cat $WORKDIR/raw/startrek_tng.csv | cut -d ! -f2- > $WORKDIR/startrek_tng.csv
