#!/bin/sh
curl ftp://ftp.irisa.fr/local/texmex/corpus/${1}.tar.gz --output ${1}.tar.gz
tar zxf ${1}.tar.gz
rm -f ${1}.tar.gz
