#!/bin/sh
TEST_WORKDIR=/tmp/jina/faiss/
mkdir -p ${TEST_WORKDIR}
cd ${TEST_WORKDIR}
curl ftp://ftp.irisa.fr/local/texmex/corpus/siftsmall.tar.gz --output siftsmall.tar.gz
tar zxf siftsmall.tar.gz
