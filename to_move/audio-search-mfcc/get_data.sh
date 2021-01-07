#!/bin/sh
TEST_WORKDIR=/tmp/jina/audio_data/
mkdir -p ${TEST_WORKDIR}
cd ${TEST_WORKDIR}
curl -L https://github.com/karoldvl/ESC-50/archive/master.zip --output audio_dataset.zip
unzip audio_dataset.zip
