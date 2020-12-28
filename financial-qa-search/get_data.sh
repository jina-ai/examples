#!/bin/sh
WORKDIR=./dataset
mkdir -p ${WORKDIR}
wget -P $WORKDIR https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/retriever/test_answers.csv
wget -P $WORKDIR https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/retriever/answer_collection.tsv
wget -P $WORKDIR https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/data/id_to_text/docid_to_text.pickle
wget -P $WORKDIR https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/data/id_to_text/qid_to_text.pickle
wget -P $WORKDIR https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/data/data_pickle/test_set_50.pickle