#!/bin/sh
DATASET="mikeortman/wikipedia-sentences"
DATA_DIR="data"
LINES=3000



cd ${DATA_DIR}
kaggle datasets download -d ${DATASET}
unzip wikipedia-sentences.zip
rm -f toy-data.txt
rm -f wikipedia-sentences.zip
mv wikisent2.txt input.txt
