#!/bin/sh
MODEL_DIR=models
DATA_DIR=data
REPO_DIR=audioset_tagging_cnn

# === Check for dirs first and get errors out of the way ===
if [ -d "$MODEL_DIR" ]; then
  echo $MODEL_DIR ' exists. Please delete it to continue'
  exit 1
fi

if [ -d "${DATA_DIR}" ]; then
  echo ${DATA_DIR} ' exists. Please delete it to continue'
  exit 1
fi
# ============ Download the model ============
echo "Downloading model"
mkdir -p ${MODEL_DIR}
echo "------ Download Vggish model ------"
curl https://storage.googleapis.com/audioset/vggish_model.ckpt --output ${MODEL_DIR}/vggish_model.ckpt
echo "------ Download PCA model ------"
curl https://storage.googleapis.com/audioset/vggish_pca_params.npz --output ${MODEL_DIR}/vggish_pca_params.npz

# ============ Download dataset ============
echo "Downloading data"
mkdir -p ${DATA_DIR}

echo "------ Download metadata ------"
git clone https://github.com/qiuqiangkong/audioset_tagging_cnn.git
cd ${REPO_DIR}
git checkout -b temp 750c318
cd ..
mkdir -p $DATA_DIR"/metadata"
wget -O $DATA_DIR"/metadata/eval_segments.csv" \
  http://storage.googleapis.com/asia_audioset/youtube_corpus/v1/csv/eval_segments.csv
# this is not so elegant but the it is hardcoded at the audio-search/audioset_tagging_cnn/utils/config.py::L8
mkdir metadata
wget -O "metadata/class_labels_indices.csv" \
  http://storage.googleapis.com/asia_audioset/youtube_corpus/v1/csv/class_labels_indices.csv
echo "Download metadata to $DATA_DIR/metadata"
echo "------ Download wavs ------"
# mimi_data is hard coded at audio-search/audioset_tagging_cnn/utils/dataset.py::L204
python3 ${REPO_DIR}/utils/dataset.py download_wavs \
  --csv_path="${DATA_DIR}/metadata/eval_segments.csv" --audios_dir=$DATA_DIR --mini_data
rm -rf ${REPO_DIR}
rm -rf metadata

