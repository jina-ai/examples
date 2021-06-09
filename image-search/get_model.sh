#!/usr/bin/env bash

MODEL_NAME="R50x1"
MODEL_DIR="pretrained"
MODEL_VAR_DIR=$MODEL_DIR/variables
mkdir -p ${MODEL_DIR}
mkdir -p ${MODEL_VAR_DIR}

curl https://storage.googleapis.com/bit_models/Imagenet21k/${MODEL_NAME}/feature_vectors/saved_model.pb --output ${MODEL_DIR}/saved_model.pb

curl https://storage.googleapis.com/bit_models/Imagenet21k/${MODEL_NAME}/feature_vectors/variables/variables.data-00000-of-00001 --output ${MODEL_VAR_DIR}/variables.data-00000-of-00001

curl https://storage.googleapis.com/bit_models/Imagenet21k/${MODEL_NAME}/feature_vectors/variables/variables.index --output ${MODEL_VAR_DIR}/variables.index