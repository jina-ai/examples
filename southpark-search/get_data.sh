#!/bin/sh
TEST_WORKDIR=/tmp/jina/southpark/
mkdir -p ${TEST_WORKDIR}
git clone https://github.com/BobAdamsEE/SouthParkData.git $TEST_WORKDIR
python prepare_data.py
