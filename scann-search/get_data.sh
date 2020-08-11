#!/bin/sh

DATA_DIR=/tmp/jina/scann/
mkdir -p ${DATA_DIR}
cd ${DATA_DIR}

curl http://ann-benchmarks.com/glove-100-angular.hdf5 --output glove_angular.hdf5
