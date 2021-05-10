#!/bin/sh
DATASET="vikashrajluhaniwal/fashion-images"
FILENAME="fashion.csv"

# Download and unzip dataset (defaults to data/ dir)
kaggle datasets download -d ${DATASET} --unzip

# Remove first line (column titles)
cd data
echo "$(tail -n +2 ${FILENAME})" > ${FILENAME}
