#!/bin/sh
TEST_WORKDIR=models
mkdir -p ${TEST_WORKDIR}
cd ${TEST_WORKDIR}
curl https://storage.googleapis.com/audioset/vggish_model.ckpt --output vggish_model.ckpt
curl https://storage.googleapis.com/audioset/vggish_pca_params.npz --output vggish_pca_params.npz
