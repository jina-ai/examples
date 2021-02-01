#!/bin/sh
MODEL_DIR=models
DATA_DIR=data
REPO_DIR=audioset_tagging_cnn

# === Check for dirs first and get errors out of the way ===
if [ -d "$MODEL_DIR" ]; then
  echo $MODEL_DIR ' exists. Please delete it to continue'
  exit 1
fi

# ============ Download the model ============
echo "Downloading model"
mkdir -p ${MODEL_DIR}
echo "------ Download Vggish model ------"
curl https://storage.googleapis.com/audioset/vggish_model.ckpt --output ${MODEL_DIR}/vggish_model.ckpt
echo "------ Download PCA model ------"
curl https://storage.googleapis.com/audioset/vggish_pca_params.npz --output ${MODEL_DIR}/vggish_pca_params.npz
