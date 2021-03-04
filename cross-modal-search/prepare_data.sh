#!/bin/sh
unzip flickr8k.zip
rm flickr8k.zip
mkdir data || true
mkdir data/f8k || true
mkdir data/images || true
mv Images data/f8k/images
mv captions.txt data/f8k/captions.txt