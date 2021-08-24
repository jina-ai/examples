#!/bin/sh
export MODEL_DIR=assets

mkdir -p ${MODEL_DIR}
if [ ! -f "${MODEL_DIR}/AudioCLIP-Full-Training.pt" ]; then
  echo "Downloading model"
  echo "------ Download AudioCLIP model ------"
  wget -q https://github.com/AndreyGuzhov/AudioCLIP/releases/download/v0.1/AudioCLIP-Full-Training.pt
  file="$(ls -lh ./)" && echo $file
  mv AudioCLIP-Full-Training.pt ${MODEL_DIR}/AudioCLIP-Full-Training.pt
  file="$(ls -lh ./assets)" && echo $file

else
  echo "Model already exists! Skipping."
fi

if [ ! -f "${MODEL_DIR}/bpe_simple_vocab_16e6.txt.gz" ]; then
  echo "Downloading vocab"
  echo "------ Download vocab ------"
  wget -q https://github.com/AndreyGuzhov/AudioCLIP/releases/download/v0.1/bpe_simple_vocab_16e6.txt.gz
  mv bpe_simple_vocab_16e6.txt.gz ${MODEL_DIR}/bpe_simple_vocab_16e6.txt.gz
else
  echo "Vocab already exists! Skipping."
fi
