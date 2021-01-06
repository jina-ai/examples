#!/bin/sh
mkdir -p dataset/
wget -P  dataset/ https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/retriever/test_answers.csv
wget -P  dataset/ https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/retriever/answer_collection.tsv
wget -P  dataset/ https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/data/id_to_text/docid_to_text.pickle
wget -P  dataset/ https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/data/id_to_text/qid_to_text.pickle
wget -P  dataset/ https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/data/data_pickle/test_set.pickle
wget -P  dataset/ https://raw.githubusercontent.com/yuanbit/FinBERT-QA/master/data/data_pickle/sample_test_set.pickle
mkdir -p model/finbert/
wget  -P model/finbert/ https://www.dropbox.com/s/3vp2fje2x0hwd84/finbert-domain.zip
cd       model/finbert/
unzip finbert-domain.zip
rm       finbert-domain.zip