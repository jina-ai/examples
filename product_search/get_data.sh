#!/bin/sh
DATASET="vikashrajluhaniwal/fashion-images"

# Download and unzip dataset (defaults to data/ dir)
kaggle datasets download -d ${DATASET} --unzip
