#!/bin/sh
JINA_TEST_WORKDIR=/tmp/jina/faiss/
mkdir -p ${JINA_TEST_WORKDIR}
cd ${JINA_TEST_WORKDIR}
curl ftp://ftp.irisa.fr/local/texmex/corpus/siftsmall.tar.gz --output siftsmall.tar.gz
tar zxf siftsmall.tar.gz
